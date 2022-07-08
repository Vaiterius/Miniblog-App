"""Routes for authentication components"""
from flask import Blueprint, render_template, redirect, request, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from blogapp import db, fc
from blogapp.models import Users

# Blueprint creation.
auth_bp = Blueprint(
    "auth_bp", __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/auth/static"
)


@auth_bp.route("/login", methods=["GET", "POST"])
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


@auth_bp.route("/signup", methods=["GET", "POST"])
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

