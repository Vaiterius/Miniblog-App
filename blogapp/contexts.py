"""Context processors and other useful functions"""
from re import template
from flask import Blueprint, current_app as app
from datetime import datetime

from blogapp import fc


contexts_bp = Blueprint("contexts_bp", __name__)


@contexts_bp.app_context_processor
def datetime_processor():
    """Inject current date/time into each template before rendering"""
    def get_datetime(time="default"):
        if time == "year":
            return str(datetime.now().year)
        return str(datetime.now())
    return dict(get_datetime=get_datetime)


@contexts_bp.app_context_processor
def form_constraints():
    """Inject form constraints into login/signup fields"""
    return {
        "min_name_length": fc["min_name_length"],
        "max_name_length": fc["max_name_length"],
        "min_username_length": fc["min_username_length"],
        "max_username_length": fc["max_username_length"],
        "min_pass_length": fc["min_pass_length"],
    }


@contexts_bp.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response