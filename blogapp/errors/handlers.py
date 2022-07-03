"""Routes for error handlers"""
from flask import Blueprint, render_template

# Blueprint creation.
errors_bp = Blueprint(
    "errors_bp", __name__,
    template_folder="templates",
    static_folder="static"
)


@errors_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template("404.html", message="Page not found"), 404


@errors_bp.app_errorhandler(500)
def internal_error(e):
    return render_template("500.html", message="Internal server error"), 500

