from flask import render_template,Blueprint,redirect,flash,request,current_app
from database.schema import db
from decorator import admin_required,login_required,csrf_protected
from werkzeug.utils import secure_filename
import os

manage_gallery_bp=Blueprint('manage_gallery',__name__)

@manage_gallery_bp.route('/admin/manage_gallery')
@login_required
@admin_required
def gallery():
    Gallery_Query=db.fetchQuery("SELECT * FROM gallery ")
    gallery=Gallery_Query
    return render_template('gallery/admin_view.html',gallery=gallery)
       
   
ALLOWED_EXTENSION = {'png','jpg','jpeg','gif','webp','avif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION




@manage_gallery_bp.route('/admin/gallery/edit-gallery/<int:id>',methods=['GET', 'POST'])
@login_required
@admin_required
@csrf_protected
def edit_gallery(id):
    CHECK_QUERY="SELECT * from gallery WHERE image_id=%s"
    gallery=db.fetchQuery(CHECK_QUERY,(id,))
    
    if not gallery:
            flash('Image not found', "danger")
            return redirect(request.url)
    gallery=gallery[0]
   
        
    
        
    if request.method=='POST':
        title=request.form.get('title')
        file = request.files.get('image')
        
        image_path = gallery['image_path'] 
        
        if file and file.filename and allowed_file(file.filename):
            if gallery['image_path']:
                old_file_path = os.path.join(current_app.static_folder, gallery['image_path'])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
               
            filename = secure_filename(f"{id}_{file.filename}")
            upload_dir = os.path.join(current_app.static_folder, 'gallery')
            os.makedirs(upload_dir, exist_ok=True)
            
            file.save(os.path.join(upload_dir, filename))
            image_path = f"gallery/{filename}"

          
            

        UPDATE_QUERY="""
                UPDATE gallery SET title=%s,image_path=%s
                WHERE image_id=%s
            """
        
       
        values=(title,image_path,id)
            
        db.executeQuery(UPDATE_QUERY,values)
        flash('Gallery edited successfully',"success")
        return redirect(request.url)
       
    
    return render_template('gallery/edit_gallery.html',gallery=gallery)
        
        


           