"""Routes for main blog components"""
from flask import (
    Blueprint,
    render_template,
    make_response,
    redirect,
    jsonify,
    flash,
    request,
    session
)

from blogapp import db
from blogapp.models import Users, Posts
from blogapp.utilities import login_required

# Blueprint creation.
main_bp = Blueprint(
    "main_bp", __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/main/static"
)


@main_bp.route("/")
@login_required
def index():
    """User's homepage after logging or signing in"""
    # Fetch posts of user and whoever the user follows.
    posts = Posts.query.all()
    return render_template("index.html", posts=posts)


@main_bp.route("/global")
def global_posts():
    """Blog posts of everyone"""
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template("global.html", posts=posts)


@main_bp.route("/create_post", methods=["GET", "POST"])
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


# @main_bp.route("/follow_unfollow", methods=["POST"])
# @login_required
# def follow_unfollow():
#     """Follow or unfollow the given user"""
#     # Receive AJAX response data for user to follow.
#     data = request.get_json(force=True)
#     user = Users.query.filter_by(username=data["username"]).first_or_404()
#     action = data["action"]
#     session_user = Users.query.get(session["user_id"])

#     # Perform desired action depending on if user is to be followed or unfollowed.
#     if not user:
#         flash("Unable to follow nonexistent user", "error")
#         return redirect("/")
    
#     if action == "follow":
#         if not session_user.is_following(user):
#             session_user.users_followed.append(user)
#             db.session.commit()
#             # flash(f"Now following {user.username}", "success")
#         # else:
#             # flash("You are already following this user", "error")
#     elif action == "unfollow":
#         if session_user.is_following(user):
#             session_user.users_followed.remove(user)
#             db.session.commit()
#             # flash(f"You have unfollowed {user.username}", "success")
#         # else:
#             # flash("You are not already following this user", "error")
#     print(data)
#     new_data = {"username": data["username"], "action": data["action"]}
#     print(new_data)
#     return make_response(jsonify(new_data), 200)


@main_bp.route("/follow_test", methods=["POST"])
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


@main_bp.route("/user/<username>")
def user(username):
    """View the profile of a user and all their blog posts"""
    user = Users.query.filter_by(username=username).first_or_404()
    session_user = None
    if session["user_id"]:
        session_user = Users.query.get(session["user_id"])
    return render_template("user.html", user=user, session_user=session_user)


@main_bp.route("/post/id=<post_id>")
def view_post(post_id):
    """View an individual blog post"""
    post = Posts.query.get(post_id)
    if post is None:
        flash("Post does not exist", "error")
        return redirect("/")
    return render_template("post.html", post=post)