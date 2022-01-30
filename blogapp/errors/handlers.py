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
    return render_template("error.html"), 404

