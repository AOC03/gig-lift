from functools import wraps
from flask import session, redirect, url_for, flash, g, abort
from .db import get_db
from .models import User, AdminUser

def load_current_user():
    user_id = session.get("user_id")
    if not user_id:
        g.user = None
        return
    [db] = list(get_db())
    try:
        g.user = db.query(User).get(user_id)
    finally:
        db.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in first.")
            return redirect(url_for("login"))

        [db] = list(get_db())
        try:
            is_admin = db.query(AdminUser).get(session["user_id"]) is not None
        finally:
            db.close()

        if not is_admin:
            abort(403)

        return view(*args, **kwargs)

    return wrapped
