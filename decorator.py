from functools import wraps
from flask import session, redirect, url_for, flash,request,abort


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("public.home")) 
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedin"):
            flash("Please log in first.", "info")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function



def csrf_protected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            token = request.form.get("_csrf_token")
            actual_session_token = session.get("_csrf_token")
            
            print(f"--- CSRF DEBUG ---")
            print(f"Token from Form: {token}")
            print(f"Token from Session: {actual_session_token}")
            
            if not token or token != actual_session_token:
                print("CSRF MATCH FAILED!")
                abort(403, description="CSRF token missing or invalid")
        return f(*args, **kwargs)
    return decorated_function
           