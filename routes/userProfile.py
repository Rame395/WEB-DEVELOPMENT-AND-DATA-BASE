from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
import os
# import imghdr
from werkzeug.utils import secure_filename
from database.schema import db
from decorator import csrf_protected,login_required

userProfile_bp = Blueprint('userProfile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024 
UPLOAD_FOLDER = 'uploads/profiles'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image(file):
    if not file or not file.filename:
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  
    
    if file_size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
  
    # file_type = imghdr.what(file)
    # if file_type not in ALLOWED_EXTENSIONS:
    #     return False, "Invalid image file"
    
    return True, None
    
    
   


def delete_old_profile_picture(user_id):
    try:
        old_profile = db.fetchQuery(
            "SELECT profile_picture FROM user_profile WHERE user_id=%s",
            (user_id,)
        )
        if old_profile and old_profile[0]['profile_picture']:
            old_path = os.path.join(current_app.root_path, old_profile[0]['profile_picture'])
            if os.path.exists(old_path):
                os.remove(old_path)
    except Exception as e:
        current_app.logger.error(f"Error deleting old profile picture: {e}")
   
        
   
def save_profile_picture(file, user_id):
 
    ext = file.filename.rsplit('.', 1)[1].lower()
    new_filename = f"{user_id}_profile.{ext}"
  
    db_path = f"uploads/profiles/{new_filename}"
  

    absolute_path = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', new_filename)
  
    os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
    
    delete_old_profile_picture(user_id)
    file.save(absolute_path)
 
    return db_path
    
    
  

@userProfile_bp.route('/Myprofile', methods=['GET','POST'])
@login_required
@csrf_protected
def userProfile():
    if 'user_id' not in session:
        flash('Please log in to access your profile', 'warning')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']

    if request.method == 'POST':
        try:
            fullName = request.form.get('fullname')
            file = request.files.get('profile_picture')

          

            image_path = None
            if file and file.filename:
                is_valid, error_msg = validate_image(file)
                if not is_valid:
                    flash(error_msg, 'error')
                    return redirect(url_for('userProfile.userProfile'))
                
                image_path = save_profile_picture(file, user_id)
                
                print(f"image path; {image_path}")

            user_exists = db.fetchQuery(
                "SELECT id FROM user_profile WHERE user_id=%s",
                (user_id,)
            )

            if user_exists:
                if image_path:
                    db.executeQuery("""
                        UPDATE user_profile
                        SET fullname=%s, profile_picture=%s
                        WHERE user_id=%s
                    """, (fullName, image_path, user_id))
                else:
                    db.executeQuery("""
                        UPDATE user_profile
                        SET fullname=%s
                        WHERE user_id=%s
                    """, (fullName, user_id))
            else:
                db.executeQuery("""
                    INSERT INTO user_profile (user_id, fullname, profile_picture)
                    VALUES (%s, %s, %s)
                """, (user_id, fullName, image_path))
                
            
            if image_path:
                session['profile_picture'] = image_path
            
            flash('Profile updated successfully', 'success')
            return redirect(url_for('userProfile.userProfile'))
        
        except Exception as e:
            current_app.logger.error(f"Error updating profile: {e}")
            flash('An error occurred while updating your profile', 'error')
            return redirect(url_for('userProfile.userProfile'))
        
    try:
        # 1. Fetch THIS specific user's info from the main users table
        user_data = db.fetchQuery("SELECT * FROM users WHERE id=%s", (user_id,))
        user = user_data[0] if user_data else None

        # 2. Fetch profile details
        profile_data = db.fetchQuery("""
            SELECT fullname, profile_picture
            FROM user_profile
            WHERE user_id=%s
        """, (user_id,))
        profile = profile_data[0] if profile_data else None

        # 3. Handle loyalty (Default to "New Member" if record doesn't exist)
        loyalty_data = db.fetchQuery("""
            SELECT loyalty_tier FROM customer_analytics 
            WHERE id=%s 
        """, (user_id,))
        
        # Safe check: if loyalty_data exists, use it; otherwise, use a default string
        level = loyalty_data[0] if loyalty_data else {'loyalty_tier': 'Bronze'}

        return render_template('users/my_profile.html', 
                               profile=profile, 
                               level=level, 
                               user=user)

    except Exception as e:
        current_app.logger.error(f"Error fetching profile: {e}")
        flash('An error occurred while loading your profile', 'error')
        # Provide empty defaults so the template doesn't crash
        return render_template('users/my_profile.html', profile=None, level={'loyalty_tier': 'New'}, user=None)
        





