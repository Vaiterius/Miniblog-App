"""Routes for main blog components"""
from flask import (
    Blueprint, Response,
    render_template, make_response, redirect, jsonify,
    flash, url_for, abort,
    request, session, current_app
)
from werkzeug.utils import secure_filename

from blogapp import db, fc
from blogapp.models import Users, Posts, PostLikes, PostComments
from blogapp.utilities import S3BucketUtils, login_required, extract_img_url,\
    extract_key_from_url, make_unique_url

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
    
    page = request.args.get("page", default=1, type=int)
    comments = PostComments.query.filter_by(post_id=post_id).order_by(
        PostComments.date_commented.desc()).paginate(
            page, current_app.config["POSTS_PER_PAGE"], False)
    
    next_url = url_for("main_bp.view_post",
        post_id=post_id, page=comments.next_num) if comments.has_next else None
    prev_url = url_for("main_bp.view_post",
        post_id=post_id, page=comments.prev_num) if comments.has_prev else None

    return render_template("post_view.html",
        post=post, session_user=session_user, comments=comments.items,
        next_url=next_url, prev_url=prev_url, indiv_view=True)


# @main_bp.route("/files")
# @login_required
# def files():
#     """View all the files uploaded on the s3 bucket"""
#     bucket = S3BucketUtils.get_bucket()
#     summaries = bucket.objects.all()

#     return render_template("files.html", bucket=bucket, files=summaries)


# @main_bp.route("/buckets", methods=["POST", "GET"])
# @login_required
# def buckets():
#     """View all the files uploaded on the s3 bucket"""
#     if request.method == "POST":
#         bucket = request.form["bucket"]
#         session["bucket"] = bucket
#         return redirect("/files")
#     else:
#         buckets = S3BucketUtils.get_bucket_list()
#         return render_template("buckets.html", buckets=buckets)


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


@main_bp.route("/create_comment/post_id=<post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    """User submits comment under post"""
    comment = request.form.get("comment").strip()
    
    # Ensure comment length adheres to the max length it can be.
    if len(comment) > fc["max_comment_length"]:
        flash(f"Comment exceeds maximum of {fc['max_comment_length']} characters!", "error")
        return redirect(f"/post/id={post_id}")
    
    user_id = session["user_id"]
    post_comment = PostComments(
        commenter_id=user_id,
        post_id=post_id,
        comment=comment
    )

    db.session.add(post_comment)
    db.session.commit()

    flash("Successfully posted comment!", "success")

    return redirect(f"/post/id={post_id}")


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


@main_bp.route("/edit_post/id=<post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    """Interface for user to edit already-existing post"""

    user_id = session["user_id"]
    post = Posts.query.get(post_id)
    current_title = post.title
    current_desc = post.description
    current_content = post.content
    
    if request.method == "POST":

        title = request.form.get("title").strip()
        desc = request.form.get("desc")
        content = request.form.get("content").strip()

        # If user has deleted some images from editing, delete those orphaned
        # images from the s3 bucket.
        old_content = set(extract_img_url(current_content))
        new_content = set(extract_img_url(content))

        orphaned_urls = (old_content ^ new_content) & old_content

        if orphaned_urls:
            bucket = S3BucketUtils.get_bucket()
            for orphan in orphaned_urls:
                key = extract_key_from_url(orphan)
                bucket.Object(key).delete()

        # Validate required fields.
        if not title or not content:
            flash("Title and content are required!", "error")
            return render_template("edit_post.html", post_id=post_id), 400
        
        # Validate title length.
        if len(title) > fc["max_title_length"]:
            flash(f"Title length exceeds {fc['max_title_length']} characters", "error")
            return render_template("edit_post.html", post_id=post_id), 400
        
        # Validate description length, if added.
        if desc:
            desc = desc.strip()
            if len(desc) > fc["max_desc_length"]:
                flash(f"Description length exceeds {fc['max_desc_length']} characters", "error")
                return render_template("edit_post.html", post_id=post_id), 400

        # Validate content length.
        if len(content) > fc["max_content_length"]:
            flash(f"Content length exceeds {fc['max_content_length']} characters", "error")
            return render_template("edit_post.html", post_id=post_id), 400
        
        post.title = title
        post.description = desc
        post.content = content
        db.session.commit()

        flash("Your post has been updated!", "success")

        return redirect(f"/post/id={post_id}")
    
    return render_template("edit_post.html", post_id=post_id,
        current_title=current_title, current_desc=current_desc, current_content=current_content)


# @main_bp.route("/upload", methods=["POST"])
# @login_required
# def upload():
#     """Upload files into the s3 bucket for image storage"""
#     file = request.files["file"]

#     bucket = S3BucketUtils.get_bucket()
#     bucket.Object(file.filename).put(Body=file)

#     flash("Uploaded!", "success")

#     return redirect(url_for("main_bp.files"))


# @main_bp.route("/delete", methods=["POST"])
# @login_required
# def delete():
#     """Delete file from s3 bucket"""
#     key = request.form["key"]

#     bucket = S3BucketUtils.get_bucket()
#     bucket.Object(key).delete()

#     flash("File deleted successfully!", "success")

#     return redirect(url_for("main_bp.files"))


# @main_bp.route("/download", methods=["POST"])
# @login_required
# def download():
#     """Download file from s3 bucket"""
#     key = request.form["key"]

#     bucket = S3BucketUtils.get_bucket()
#     file_object = bucket.Object(key).get()

#     return Response(
#         file_object["Body"].read(),
#         mimetype="text/plain",
#         headers={"Content-Disposition": f"attachment;filename={key}"}
#     )


@main_bp.route("/upload_image", methods=["POST"])
@login_required
def upload_image():
    """Store file temporarily in folder before uploading to s3 bucket"""
    file = request.files.get("file")

    # Validate filesize, max 2MB.

    if file:
        filename = secure_filename(file.filename).lower()
        filename = make_unique_url(filename)

        # Get accessable s3 URL for uploaded image.
        location = S3BucketUtils.get_s3_session().client("s3").generate_presigned_url(
            "get_object", Params={
                "Bucket": current_app.config["S3_BUCKET"],
                "Key": filename}
        )

        # Place image in bucket.
        bucket = S3BucketUtils.get_bucket()
        bucket.Object(filename).put(Body=file)
        
        return jsonify({"location": location})

    return abort(Response("500 - image failed to upload"))


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
    
    # Also delete any likes and comments associated with the post.
    PostLikes.query.filter_by(post_id=post_id).delete()
    PostComments.query.filter_by(post_id=post_id).delete()

    # Delete any images stored on the s3 bucket.
    content = post.content
    urls = extract_img_url(content)
    bucket = S3BucketUtils.get_bucket()

    for url in urls:
        key = extract_key_from_url(url)
        bucket.Object(key).delete()

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted!", "success")

    return redirect("/")


@main_bp.route("/delete_comment/id=<comment_id>")
@login_required
def delete_comment(comment_id):
    """User deletes own comment"""
    comment = PostComments.query.get(comment_id)

    # Ensure comment can only be deleted by its author or the post author.
    if comment.commenter_id != session["user_id"] and comment.post.author_id != session["user_id"]:
        flash("Cannot delete comment", "error")
        return redirect(f"/post/id={comment.post_id}")
    
    db.session.delete(comment)
    db.session.commit()

    flash("Comment deleted!", "success")

    return redirect(f"/post/id={comment.post_id}")

