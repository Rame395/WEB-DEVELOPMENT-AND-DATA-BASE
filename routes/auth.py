from flask import Blueprint,render_template,url_for,session,flash,redirect,current_app,request,make_response
from flask_mail import Message
from werkzeug.security import generate_password_hash,check_password_hash
from itsdangerous import URLSafeTimedSerializer,SignatureExpired,BadSignature
from datetime import datetime, timedelta
from database.schema import db
from time import time
import secrets
import re
from app import mail
from decorator import csrf_protected,login_required





auth_bp=Blueprint("auth",__name__)



def get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def strong_password(pwd):
    return (
        len(pwd)>=8 and
        re.search(r'[A-Z]',pwd) and
        re.search(r'[a-z]',pwd) and
        re.search(r'[0-9]',pwd) and
        re.search(r"[!@#$%^&*]", pwd)
    )
    
def send_login_alert(user_email, device, location_link):
    msg = Message('New Login Alert - world Hotels',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user_email])
    
    msg.body = f""" Hi there, A new login was detected for your account. DEVICE INFO: {device} LOCATION: {location_link}If this was not you, please reset your password immediately."""
    mail.send(msg)
    

    
    
RATE_LIMIT={}
MAX_REQUESTS=5
WINDOW_SECONDS=900 

def is_rate_limit(ip):
    now=time()
    timestamp=RATE_LIMIT.get(ip,[])
    
    timestamp=[t for t in timestamp if now -t <WINDOW_SECONDS]
    
    
    if len(timestamp)>=MAX_REQUESTS:
        return True
    timestamp.append(now)
    RATE_LIMIT[ip]=timestamp
    return False



@auth_bp.route('/auth', methods=["GET"])
@csrf_protected
def auth():
    return render_template('authentication/auth.html')

    
@auth_bp.route('/auth/signup',methods=["GET","post"])
def signup():
   
    if request.method=="POST":
        try:
            username=request.form.get("username2")
            email=request.form.get("email2")
            password=request.form.get("password2")
            confirmPassword=request.form.get("confirmPassword")
            
            if not username or not email or not password:
                flash("All field are required","danger")
                return redirect(url_for("auth.signup"))
            
            if not is_valid_email(email):
                flash("Invalid Email Format")
                return redirect(url_for("auth.signup"))
            
        
            if not strong_password(password):
                flash('Password must be strong',"danger")
                return redirect(request.url)
            
            if password!=confirmPassword:
                flash("Password does not matched")
                return redirect(url_for("auth.signup"))
            
            
            user= db.fetchQuery(
                "SELECT id FROM users WHERE email=%s OR username=%s",
                (email, username)
            )

            if user:
                flash("Account already exists","warning")
                return redirect(url_for("auth.signup"))

            hashed_password = generate_password_hash(password)
            try:
                db.executeQuery(
                        "INSERT INTO users (username, email, password, status) VALUES (%s, %s, %s, 0)",
                        (username, email, hashed_password)
                    )
                
                token = get_serializer().dumps(email, salt="email-confirm")
                link = url_for("auth.activate_account", token=token, _external=True)
                print("ACTIVATION LINK:", link)

                msg = Message("Activate Your Account", recipients=[email])
                msg.body = f"""Hello {username}, Click the link below to activate your account: {link} This link expires in 1 hour."""
                mail.send(msg)
                flash("Check your email to activate your account", "success")
            
            
            except Exception as e:
                flash("There was an error sending the activation email. Please try again.", "danger")
            return redirect(url_for("auth.signup"))
        
        except Exception as e:
            current_app.logger.error(f"Error updating profile: {e}")
            flash('Some thing went wrong! Please try again', 'error')
            return redirect(url_for('auth.login'))
            
    
    return render_template("authentication/auth.html")
    




@auth_bp.route("/activate/<token>")
def activate_account(token):
    try:
        email = get_serializer().loads(token, salt="email-confirm", max_age=3600)
        
       
        result = db.executeQuery(
            "UPDATE users SET status=1, role='user' WHERE email=%s AND status=0",
            (email,)
        )
        
        return render_template("authentication/activation_status.html", 
                               success=True, 
                               message="Your account is now active! Redirecting to login...")
                               
    except SignatureExpired:
        return render_template("authentication/activation_status.html", 
                               success=False, 
                               message="The activation link has expired. Please register again.")
    except BadSignature:
        return render_template("authentication/activation_status.html", 
                               success=False, 
                               message="The activation link is invalid.")



MAX_ATTEMPTS=5
LOCK_TIME=timedelta(minutes=15)

    
    
    
@auth_bp.route("/auth/login",methods=["GET","POST"])
@csrf_protected
def login():
    if request.method=="POST":
        username=request.form.get("username1")
        password=request.form.get("password1")
        remember = request.form.get('remember')
        device = request.form.get('device_info')
        lat = request.form.get('user_lat')
        lon = request.form.get('user_lon')
        
        
        if not username or not password:
            flash("All field are required","danger")
            return redirect(url_for("auth.login"))
        
        user_list=db.fetchQuery("SELECT * FROM users WHERE username=%s AND status=%s", (username,1))
        
       
       
        if not user_list:
                flash("Invalid username or password", "danger")
                return redirect(url_for("auth.login"))
        
        user=user_list[0]
       
        now=datetime.now()
        
        if user['lock_until'] and user['lock_until']>now:
            remaining=int((user['lock_until']-now).total_seconds()/60)
            flash(f"Account locked. Try again in {remaining} minutes.", "danger")
            return redirect(request.url)
        
        if not check_password_hash(user['password'],password):
            failed_attempts=user['failed_attempts']+1
            
            if failed_attempts>=MAX_ATTEMPTS:
                lock_until=now+LOCK_TIME
                
                db.executeQuery("""
                        UPDATE users
                        SET failed_attempts=%s,lock_until=%s
                        WHERE id=%s
                        """,(failed_attempts,lock_until,user['id']))
                flash("Too many failed attempts. Account locked for 15 minutes.", "danger")
                
            else:
                db.executeQuery("""
                          UPDATE users
                          set failed_attempts=%s,last_failed_at=%s
                          WHERE id=%s
                        """,(failed_attempts,now,user['id']))
                remaining=MAX_ATTEMPTS-failed_attempts
                flash("Invalid username or password", "danger")
                
                if remaining>4:
                  flash(f"Wrong password. {remaining} attempts left.", "warning")
            
            return redirect(request.url)
        
        
        db.executeQuery("""
                    UPDATE users SET failed_attempts=0,lock_until=Null
                    WHERE id=%s
            """,(user['id'],))
       
        session["loggedin"]=True
        session["user_id"]=user["id"]
        session['email']=user['email']
        session["username"]=user["username"]
        session["role"]=user["role"]
        session.permanent = True
        profile = db.fetchQuery("""
                        SELECT profile_picture FROM user_profile WHERE user_id=%s""", (user['id'],))
        if profile and profile[0]['profile_picture']:
            session['profile_picture'] = profile[0]['profile_picture']
        else:
            session['profile_picture'] = 'uploads/profiles/default_profile.avif'
      
        
        
        
        if user["role"]=="admin":
            target_url=(url_for("dashboard.admin_dashboard"))
        else:
            target_url=(url_for("dashboard.user_dashboard"))
        
        
        
        resp = make_response(redirect(target_url))

        
            
            
        if remember:
            token = secrets.token_hex(32)
            db.executeQuery("UPDATE users SET token = %s WHERE id = %s", (token, user['id']))
            db.commit()
            resp.set_cookie(
                    'remember_me',
                    token,
                    max_age=30*24*60*60,
                    httponly=True,
                    samesite='Lax',
                    path='/'
                )
            
          
            db_token = db.fetchQuery("SELECT token FROM users WHERE id=%s", (user['id'],))[0]['token']
            print("Token in DB:", db_token)
            print("Token in cookie:", request.cookies.get('remember_me'))
            print("Match?", db_token == request.cookies.get('remember_me'))

    
           
           
        if user:
           map_link = f"https://www.google.com/maps?q={lat},{lon}" if lat else "Unknown Location"
           send_login_alert(user['email'], device, map_link)
        
         
        flash("Login successful", "success")
        return resp
   
    username = ""
    token = request.cookies.get("remember_me")
    print(f"-------------------------: {token}")
    if token:
        user_list = db.fetchQuery("SELECT * FROM users WHERE token = %s AND status = 1", (token,))
        if user_list:
                    username = user_list[0]["username"]
                    
    print(f"Prefilled Username: {username}")
            
    return render_template('authentication/auth.html',username=username) 




               
    
       
       
        
@auth_bp.route("/auth/logout")
def logout():
    if "user_id" in session:
        db.executeQuery("UPDATE users SET token = NULL WHERE id = %s", (session["user_id"],))
        db.commit()
    session.clear()

    resp = make_response(redirect(url_for("auth.login")))
    resp.delete_cookie("remember_me", path='/')  
    flash("You have been logged out successfully.", "info")
    return resp







    
@auth_bp.route('/auth/forget_password',methods=['GET','POST'])
@csrf_protected
def forget_Password():
    if request.method=='POST':
        ip=request.remote_addr
        
        if is_rate_limit(ip):
            flash("Too many request try again later.", "danger")
            return redirect(request.url)
        
        
        email=request.form.get('email')
        
        user=db.fetchQuery("SELECT id from users WHERE email=%s",(email,))
        if not user:
            flash("If the email exists, a reset link has been sent.", "info")
            return redirect(request.url)
        
        token=secrets.token_urlsafe(32)
        expires=datetime.now()+timedelta(minutes=15)
        
        db.executeQuery("""
                  UPDATE users SET reset_token=%s,reset_expires=%s      
                  WHERE email=%s""",(token,expires,email))
        
        reset_link = url_for('auth.reset_password', token=token, _external=True)

        msg = Message("Reset Your Password", recipients=[email])
        msg.body=f"""Click the Link below to reset the password: \n {reset_link}\n This link will expire in 15 minute"""
        mail.send(msg)
        
        flash("If the email exists, a reset link has been sent.", "info")
        return redirect(url_for('auth.login'))
    
    return render_template('authentication/forget_password.html')




@auth_bp.route('/auth/reset_password/<token>', methods=['POST','GET'])
@csrf_protected
def reset_password(token):
    user=db.fetchQuery("""
                SELECT id from users WHERE reset_token=%s AND reset_expires>NOW()
                """,(token,))
    print(f"ID: {user}")
    if not user:
        flash("Invalid or expired token","danger")
        return(redirect(url_for('auth.login')))
    
    if request.method=="POST":
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        
        if password!=confirm_password:
            flash("Password do not match", "danger")
            return redirect(request.url)
        
        if not strong_password(password):
            flash("Password must be strong", "danger")
            return redirect(request.url)
        
        hashed_password=generate_password_hash(password)
        
        user_id=user[0]['id']  
        db.executeQuery("""
                    UPDATE users SET password=%s,reset_token=Null,reset_expires=Null 
                    WHERE id=%s""",(hashed_password,user_id)) 
        
        flash("password reset successfylly", "success")
        return redirect(url_for('auth.login'))
    
    return render_template('authentication/reset_password.html')



from werkzeug.security import generate_password_hash, check_password_hash

@auth_bp.route('/change-password', methods=['POST'])
@login_required
@csrf_protected
def change_password():
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    user_id = session.get('user_id')

    
    results = db.fetchQuery("SELECT password FROM users WHERE id = %s", (user_id,))
    if not results:
        flash("User not found", "danger")
        return redirect(url_for('userProfile.userProfile'))

    user = results[0]
    
    
    password = user['password']

    if not check_password_hash(password, current_pass):
        flash("Current password incorrect", "danger")
        return redirect(url_for('userProfile.userProfile'))

   
    new_hashed_pass = generate_password_hash(new_pass)
    
        
    try:
        db.executeQuery("UPDATE users SET password = %s WHERE id = %s", (new_hashed_pass, user_id))
        flash("Password updated successfully!", "success")
    except Exception as e:
        print(f"Error: {e}") 
        flash("An error occurred while updating the password.", "danger")

    return redirect(url_for('userProfile.userProfile'))

        
    
    
@auth_bp.route('/delete-account', methods=['POST'])
@login_required
@csrf_protected 
def delete_account():
    user_id = session.get('user_id')
    
    try:
       
        db.executeTransaction("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        
        session.clear()
        flash("Your account and all associated data have been permanently deleted.", "success")
        return redirect(url_for('public.home'))
    except Exception as e:
        db.rollback()
        flash("An error occurred during account deletion.", "danger")
        return redirect(url_for('userProfile.my_profile'))


        
            
   

     
            
        
        
       
        
        
        
        
    