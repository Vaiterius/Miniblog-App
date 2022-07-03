"""Context processors and other useful functions"""
from flask import Blueprint, session
from datetime import datetime

from blogapp import fc, db
from blogapp.models import Users


contexts_bp = Blueprint("contexts_bp", __name__)


@contexts_bp.app_context_processor
def form_constraints():
    """Inject form constraints into login/signup fields"""
    return fc


@contexts_bp.before_app_request
def before_request():
    """Track last time a user was online (sent a request)"""
    if not session.get("user_id"):
        return

    session_user = Users.query.get(session["user_id"])
    session_user.last_seen = datetime.utcnow()
    db.session.commit()


@contexts_bp.after_app_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response