"""Routes for main blog components"""
from flask import (
    Blueprint,
    render_template, make_response, redirect, jsonify,
    flash, url_for,
    request, session, current_app
)

from blogapp import db, fc
from blogapp.models import Users, Posts, PostLikes
from blogapp.utilities import login_required

# Blueprint creation.
main_bp = Blueprint(
    "main_bp", __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/main/static"
)


#[-------------------------------------------------------------------]
# TEMPLATE VIEWS
#[-------------------------------------------------------------------]


@main_bp.route("/")
@main_bp.route("/index")
@login_required
def index():
    """User's homepage after logging or signing in"""
    # Fetch posts of user and whoever the user follows.
    session_user = Users.query.get(session["user_id"])

    page = request.args.get("page", default=1, type=int)  # Pagination.
    posts = session_user.followed_posts(is_descending=True).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False)
    
    next_url = url_for("main_bp.index", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main_bp.index", page=posts.prev_num) if posts.has_prev else None

    return render_template( "index.html",
        title="Home", posts=posts.items, next_url=next_url, prev_url=prev_url)


@main_bp.route("/global")
def global_posts():
    """Blog posts of everyone"""
    page = request.args.get("page", default=1, type=int)  # Pagination.
    posts = Posts.get_posts(is_descending=True).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False)
    
    next_url = url_for("main_bp.global_posts", page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main_bp.global_posts", page=posts.prev_num) if posts.has_prev else None

    return render_template( "index.html",
        title="Global", posts=posts.items, next_url=next_url, prev_url=prev_url)


@main_bp.route("/user/<username>")
def user(username):
    """View the profile of a user and all their blog posts"""
    user = Users.query.filter_by(username=username).first_or_404()
    session_user = None
    if session.get("user_id"):
        session_user = Users.query.get(session["user_id"])

    page = request.args.get("page", default=1, type=int)
    posts = user.own_posts(is_descending=True).paginate(
        page, current_app.config["POSTS_PER_PAGE"], False)

    next_url = url_for("main_bp.user",
        username=username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for("main_bp.user",
        username=username, page=posts.prev_num) if posts.has_prev else None

    return render_template("user.html",
        user=user, session_user=session_user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@main_bp.route("/post/id=<post_id>")
def view_post(post_id):
    """View an individual blog post"""
    post = Posts.query.get(post_id)
    if post is None:
        flash("Post does not exist", "error")
        return redirect("/")
    session_user = None
    if session.get("user_id"):
        session_user = Users.query.get(session["user_id"])
    return render_template("post_view.html", post=post, session_user=session_user, indiv_view=True)


#[-------------------------------------------------------------------]
# FORMS
#[-------------------------------------------------------------------]


@main_bp.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    """An editable interface for the User to upload to their own blog"""
    if request.method == "POST":

        user_id = session["user_id"]
        title = request.form.get("title").strip()
        desc = request.form.get("desc")
        content = request.form.get("content").strip()

        # Validate required fields.
        if not title or not content:
            flash("Title and content are required!", "error")
            return render_template("create_post.html"), 400
        
        # Validate title length.
        if len(title) > fc["max_title_length"]:
            flash(f"Title length exceeds {fc['max_title_length']} characters", "error")
            return render_template("create_post.html"), 400
        
        # Validate description length, if added.
        if desc:
            desc = desc.strip()
            if len(desc) > fc["max_desc_length"]:
                flash(f"Description length exceeds {fc['max_desc_length']} characters", "error")
                return render_template("create_post.html"), 400

        # Validate content length.
        if len(content) > fc["max_content_length"]:
            flash(f"Content length exceeds {fc['max_content_length']} characters", "error")
            return render_template("create_post.html"), 400
        
        new_post = Posts(
            author_id=user_id,
            title=title,
            description=desc,
            content=content
        )

        db.session.add(new_post)
        db.session.commit()

        flash("Your post has been uploaded", "success")

        return redirect("/")

    return render_template("create_post.html")


@main_bp.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    """An editable interface for User to edit their profile info"""
    user_id = session["user_id"]
    user = Users.query.get(user_id)
    current_username = user.username
    current_about_me = user.about_me

    if request.method == "POST":
        username = request.form.get("username").strip()
        about_me = request.form.get("about_me").strip()

        # Check if forms are filled.
        if not username:
            flash("Must have at least a username!", "error")
            return redirect("/edit_profile")
        
        # Check valid username length.
        if len(username) < fc["min_username_length"] or len(username) > fc["max_username_length"]:
            flash("Username must be between 3 and 32 characters long!", "error")
            return redirect("/edit_profile")
        
        # Check if username already exists.
        check_username = None
        if current_username != username:  # Don't have to check if username is the same.
            check_username = Users.query.filter(Users.username.like(username)).first()
        if check_username:
            flash("Username already exists", "error")
            return redirect("/edit_profile")
        
        # Check valid about me length.
        if len(about_me) > fc["max_bio_length"]:
            flash("Bio should not exceed 140 characters!", "error")
            return redirect("/edit_profile")

        user.username = username
        user.about_me = about_me
        db.session.commit()
        
        flash("Your profile has been edited", "success")

        return redirect("/profile")

    return render_template(
        "edit_profile.html",
        current_username=current_username,
        current_about_me=current_about_me)


#[-------------------------------------------------------------------]
# NON-TEMPLATE REQUESTS & REDIRECTIONS
#[-------------------------------------------------------------------]


@main_bp.route("/follow_user", methods=["POST"])
@login_required
def follow_user():
    """Process request when user is followed by another user"""
    data = request.get_json(force=True)
    followed_user = Users.query.filter_by(id=data["followed_id"]).first_or_404()
    session_user = Users.query.get(session["user_id"])

    if not followed_user:
        flash("Unable to follow nonexistent user", "error")
        return redirect("/")
    
    new_data = dict()

    if not session_user.is_following(followed_user):
        session_user.users_followed.append(followed_user)
        new_data["performed"] = "followed"
    else:
        session_user.users_followed.remove(followed_user)
        new_data["performed"] = "unfollowed"

    db.session.commit()
    
    return make_response(jsonify(new_data))


@main_bp.route("/like_post", methods=["POST"])
@login_required
def like_post():
    """Process request when post is liked by user"""
    data = request.get_json(force=True)
    post_like = PostLikes.query.filter_by(post_id=data["post_id"], liker_id=session["user_id"]).first()
    session_user = Users.query.get(session["user_id"])

    new_data = dict()

    if session_user.has_liked(data["post_id"]):
        db.session.delete(post_like)
        new_data["liked"] = False

    else:
        post_like = PostLikes(post_id=data["post_id"], liker_id=session["user_id"])
        db.session.add(post_like)
        new_data["liked"] = True

    db.session.commit()

    post = Posts.query.get(data["post_id"])
    new_data["num_likes"] = post.likes.count()

    return make_response(jsonify(new_data))


@main_bp.route("/profile")
def profile():
    """After clicking to visit their own profile"""
    session_user = None
    if session.get("user_id"):
        session_user = Users.query.get(session["user_id"])
    return redirect(f"/user/{session_user.username}")


@main_bp.route("/delete_post/id=<post_id>")
@login_required
def delete_post(post_id):
    """User deletes own post"""
    post = Posts.query.get(post_id)

    # Ensure post can only be deleted by its owner.
    if post.author_id != session["user_id"]:
        flash("Cannot delete post", "error")
        return redirect("/")

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted!", "success")

    return redirect("/")

