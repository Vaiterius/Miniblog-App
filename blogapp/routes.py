from dataclasses import dataclass
from datetime import datetime

from flask import render_template, request, session, redirect, flash, url_for, jsonify, make_response, abort
from werkzeug.security import check_password_hash, generate_password_hash

from blogapp import app, db, form_constraints as fc
from blogapp.db_models import Users, Posts
from blogapp.utilities import login_required


#--- APP HELPERS ---#

@app.context_processor
def datetime_processor():
    """Inject current date/time into each template before rendering"""
    def get_datetime(time="default"):
        if time == "year":
            return str(datetime.now().year)
        return str(datetime.now())
    return dict(get_datetime=get_datetime)


@app.context_processor
def form_constraints():
    """Inject form constraints into login/signup fields"""
    return {
        "min_name_length": fc["min_name_length"],
        "max_name_length": fc["max_name_length"],
        "min_username_length": fc["min_username_length"],
        "max_username_length": fc["max_username_length"],
        "min_pass_length": fc["min_pass_length"],
    }


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.errorhandler(404)
def page_not_found(e):
    return "lol not found", 404


#--- MAIN ---#

@app.route("/")
@login_required
def index():
    """User's homepage after logging or signing in"""
    # Fetch posts of user and whoever the user follows.
    posts = Posts.query.all()
    return render_template("index.html", posts=posts)


@app.route("/global")
def global_posts():
    """Blog posts of everyone"""
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("global.html", posts=posts)


@app.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    """An editable interface for the User to upload to their own blog"""
    if request.method == "POST":

        user_id = session["user_id"]
        title = request.form.get("title").strip()
        content = request.form.get("content").strip()

        if not title or not content:
            flash("Must fill in all fields!", "error")
            return render_template("create_post.html"), 400
        
        # if len(title) < 10:
        #     flash("Title must have at least 10 characters", "error")
        #     return render_template("create_post.html"), 400
        # if len(content) < 100:
        #     flash("Content must have at least 100 characters", "error")
        #     return render_template("create_post.html"), 400
        
        new_post = Posts(
            author_id=user_id,
            title=title,
            content=content
        )

        db.session.add(new_post)
        db.session.commit()

        flash("Your post has been uploaded", "success")

        return redirect("/")

    return render_template("create_post.html")

@app.route("/follow_unfollow", methods=["POST"])
@login_required
def follow_unfollow():
    """Follow or unfollow the given user"""
    # Receive AJAX response data for user to follow.
    data = request.get_json(force=True)
    user = Users.query.filter_by(username=data["username"]).first_or_404()
    action = data["action"]
    session_user = Users.query.get(session["user_id"])

    # Perform desired action depending on if user is to be followed or unfollowed.
    if not user:
        flash("Unable to follow nonexistent user", "error")
        return redirect("/")
    
    if action == "follow":
        if not session_user.is_following(user):
            session_user.users_followed.append(user)
            db.session.commit()
            # flash(f"Now following {user.username}", "success")
        # else:
            # flash("You are already following this user", "error")
    elif action == "unfollow":
        if session_user.is_following(user):
            session_user.users_followed.remove(user)
            db.session.commit()
            # flash(f"You have unfollowed {user.username}", "success")
        # else:
            # flash("You are not already following this user", "error")
    print(data)
    new_data = {"username": data["username"], "action": data["action"]}
    print(new_data)
    return make_response(jsonify(new_data), 200)


@app.route("/follow_test", methods=["POST"])
@login_required
def follow_test():
    data = request.get_json(force=True)
    user = Users.query.filter_by(username=data["username"]).first_or_404()
    session_user = Users.query.get(session["user_id"])

    if not user:
        flash("Unable to follow nonexistent user", "error")
        return redirect("/")
    
    new_data = dict()

    if not session_user.is_following(user):
        session_user.users_followed.append(user)
        new_data["performed"] = "followed"
    else:
        session_user.users_followed.remove(user)
        new_data["performed"] = "unfollowed"

    db.session.commit()
    
    return make_response(jsonify(new_data))


@app.route("/user/<username>")
def user(username):
    """View the profile of a user and all their blog posts"""
    user = Users.query.filter_by(username=username).first_or_404()
    session_user = None
    if session["user_id"]:
        session_user = Users.query.get(session["user_id"])
    return render_template("user.html", user=user, session_user=session_user)


@app.route("/post/id=<post_id>")
def post_view(post_id):
    """View an individual blog post"""
    post = Posts.query.get(post_id)
    if post is None:
        flash("Post does not exist", "error")
        return redirect("/")
    return render_template("post.html", post=post)


#--- AUTHENTICATION ---#

@app.route("/login", methods=["GET", "POST"])
def login():
    """User logs in to their account"""

    # Forget any cookies.
    session.clear()

    if request.method == "POST":

        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        # At least one of the fields have not been filled in.
        if not username or not password:
            flash("Must fill in all fields!", "error")
            return render_template("login.html"), 400
        
        # Ensure username exists in database, case-insensitively.
        found_user = Users.query.filter(Users.username.like(username)).first()

        if found_user is None:
            flash("Username not found", "error")
            return render_template("login.html"), 400
        
        # Ensure password is correct.
        if not check_password_hash(found_user.get_hash(), password):
            flash("Incorrect password", "error")
            return render_template("login.html"), 400
        
        # User has successfully inputted their correct info, so log in.
        session["user_id"] = found_user.id
        session["username"] = found_user.username

        flash("You have logged in", "info")

        return redirect("/")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User creates an account"""
    
    # Forget any cookies.
    session.clear()

    if request.method == "POST":

        first_name = request.form.get("first-name").strip()
        last_name = request.form.get("last-name").strip()
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        password_again = request.form.get("password-again").strip()

        # At least one of the fields have not been filled in.
        if not first_name or not last_name or not username \
            or not password or not password_again:
            flash("Must fill in all fields!", "error")
            return render_template("signup.html"), 400
        
        # Enforce form constraints such as min and max lengths.
        if len(first_name) < fc["min_name_length"] or len(first_name) > fc["max_name_length"]:
            flash(f"Please keep name to be between {fc['min_name_length']} and {fc['max_name_length']} chars", "error")
            return render_template("signup.html"), 400
        if len(username) < fc["min_username_length"] or len(username) > fc["max_username_length"]:
            flash(f"Please keep username to be between {fc['min_username_length']} and {fc['max_username_length']} chars", "error")
            return render_template("signup.html"), 400
        if len(password) < fc["min_pass_length"]:
            flash(f"Password must be minimum of {fc['min_pass_length']} characters", "error")
            return render_template("signup.html"), 400
        
        # Ensure passwords match.
        if password != password_again:
            flash("Passwords do not match", "error")
            return render_template("signup.html"), 400
        
        # Query database and see if username already exists, case-insensitively.
        check_username = Users.query.filter(Users.username.like(username)).first()
        if check_username:
            flash("Username already exists", "error")
            return render_template("signup.html"), 400
        
        # All is well otherwise so create the user in the database and log in.
        new_user = Users(
            username=username,
            first_name=first_name,
            last_name=last_name,
            hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        # This has to go after the session add and commit for some reason.
        session["user_id"] = new_user.id
        session["username"] = new_user.username

        flash("You have successfully signed up", "success")

        return redirect("/")

    return render_template("signup.html")

