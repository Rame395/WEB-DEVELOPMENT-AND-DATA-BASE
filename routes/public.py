from flask import Blueprint,render_template,request,flash,current_app,redirect,url_for
from app import mail
from decorator import csrf_protected
from flask_mail import Message
from database.schema import db

public_bp=Blueprint("public",__name__)

@public_bp.route('/')
@public_bp.route('/home')
def home():
    return render_template('home.html')

@public_bp.route('/about-us')
def about_us():
    return render_template('about_us.html')



@public_bp.route('/contactUs', methods=['POST', 'GET'])
@csrf_protected
def contact_us():
    if request.method == 'POST':
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        msg = Message(
            subject=f"New contact form submission from {firstName}",
            recipients=[current_app.config['MAIL_USERNAME']],
            reply_to=email,
            body=f"From: {firstName} {lastName}\nPhone: {phone}\nEmail: {email}\n\nMessage:\n{message}"
        )
        
        try:
            mail.send(msg)
            flash("Message sent successfully! We will get back to you soon.", "success")
        except Exception as e:
            print(f"Mail Error: {e}")
            flash("Failed to send message. Please check your connection or try again later.", "danger")
        
       
        return redirect(url_for('public.contact_us'))
        
    return render_template('contact_us.html')


@public_bp.route('/privacy')
def privacy_policy():
    return render_template('privacy.html')

@public_bp.route('/term_of_services')
def term_of_services():
    return render_template('term_of_services.html')


@public_bp.route('/cookie-policy')
def cookie_policy():
    return render_template('cookie_policy.html')

@public_bp.route('/FAQ')
def FAQ():
    return render_template('faq.html')

@public_bp.route('/gallery')
def gallery():
    Gallery_Query=db.fetchQuery("SELECT * FROM gallery ")
    gallery=Gallery_Query
    return render_template('gallery/user_view.html',gallery=gallery)



        
    
       
        
   
        
    