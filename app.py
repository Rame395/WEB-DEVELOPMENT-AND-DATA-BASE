from flask import Flask,session,request
import secrets
from config import Config
from flask_mail import Mail
from database.schema import db

mail=Mail()


def create_app():
    app=Flask(__name__,template_folder='templates',static_folder='static',static_url_path='/')
    app.config.from_object(Config)
    from datetime import timedelta
    app.permanent_session_lifetime = timedelta(days=30)
    
    
  
    @app.before_request
    def load_user_and_csrf():
        if "user_id" not in session:
            token = request.cookies.get("remember_me")
           
            if token:
                user_list = db.fetchQuery(
                    "SELECT * FROM users WHERE token = %s AND status = 1",
                    (token,)
                )
                if user_list:
                    user = user_list[0]
                    # Preserve CSRF token
                    csrf_token = session.get("_csrf_token")
                    session.clear()
                    if csrf_token:
                        session["_csrf_token"] = csrf_token

                    session["loggedin"] = True
                    session["user_id"] = user["id"]
                    session["email"] = user["email"]
                    session["username"] = user["username"]
                    session["role"] = user["role"]
                    session.permanent = True

        # --- CSRF token ---
        if "_csrf_token" not in session:
            session["_csrf_token"] = secrets.token_hex(16)
            
            



    mail.init_app(app)
    
    from routes.public import public_bp
    app.register_blueprint(public_bp)
    
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from routes.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from routes.search import search_bp
    app.register_blueprint(search_bp)
    
    from routes.admin_dashboard.manage_user import manage_user_bp
    app.register_blueprint(manage_user_bp)
    
    from routes.userProfile import userProfile_bp
    app.register_blueprint(userProfile_bp)
    
    from routes.admin_dashboard.manage_hotel import manage_hotel_bp
    app.register_blueprint(manage_hotel_bp)
    

    
    from routes.booking import booking_bp
    app.register_blueprint(booking_bp)
    
    from routes.admin_dashboard.reports import report_bp
    app.register_blueprint(report_bp)
    
    from routes.admin_dashboard.booking_details import booking_details_bp
    app.register_blueprint(booking_details_bp)
    
    from routes.admin_dashboard.manage_room import manageRooms_bp
    app.register_blueprint(manageRooms_bp)
    
    from routes.payment_gateway import payment_bp
    app.register_blueprint(payment_bp)
    
    from routes.admin_dashboard.admin_base import adminPanel_bp
    app.register_blueprint(adminPanel_bp)
    
    
    from routes.admin_dashboard.manage_gallery import manage_gallery_bp
    app.register_blueprint(manage_gallery_bp)
    
    
    from routes.Errors_handler.errors import register_error_handlers
    register_error_handlers(app)
    
    from routes.admin_dashboard.manage_currency import manage_currency_bp
    app.register_blueprint(manage_currency_bp)
   
    
    return app
   
    
    




















