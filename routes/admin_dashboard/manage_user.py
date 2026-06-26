from flask import Blueprint,render_template,flash,redirect,session,url_for,request
from decorator import admin_required,login_required,csrf_protected
from werkzeug.security import generate_password_hash


from database.schema import db

manage_user_bp=Blueprint('manage_user',__name__)



@manage_user_bp.route('/admin/manage_user')
@admin_required
@login_required
def manage_users():
    USER_LIST_QUERY = """
        SELECT id, username, email, status, role FROM users
    """
    users = db.fetchQuery(USER_LIST_QUERY)

    COUNT_QUERY = "SELECT COUNT(*) AS total FROM users"
    total_users = db.fetchQuery(COUNT_QUERY)[0]['total']

    return render_template(
        'admin/user_management/manage-users.html',
        users=users,
        total_users=total_users
    )
    
    
  

   
    
@manage_user_bp.route('/admin/manage_user/add_user',methods=['GET','POST'])
@login_required
@admin_required
@csrf_protected
def add_user():
    if request.method=='POST':
        username=request.form.get('username').strip()
        email=request.form.get('email').strip()
        role=request.form.get('role')
        password=request.form.get('password')
        
        if not all([username, email, role, password]):
            flash("All fields are required", "warning")
            return redirect(url_for('manage_user.add_user'))
        
        CHECK_QUERY="""
            SELECT id from users WHERE email=%s OR username=%s
        """
        if db.fetchQuery(CHECK_QUERY,(email,username)):
            flash("Username or Email already exists", "danger")
            return redirect(url_for('manage_user.add_user'))
        
        hashed_password = generate_password_hash(password)
        status = 1
            
        
        INSERT_QUERY = """
            INSERT INTO users (username, email, role, password, status)
            VALUES (%s, %s, %s, %s, %s)
        """
        db.executeQuery(
            INSERT_QUERY,
            (username, email, role, hashed_password, status)
        )
        
        flash("User added successfully", "success")
        return redirect(url_for('manage_user.manage_users'))
    
    return render_template('admin/user_management/add-users.html')



# Delete User
 
@manage_user_bp.route('/admin/manage_user/delete/<int:id>')
@login_required
@admin_required
@csrf_protected
def delete_user(id):
    
    if id == session.get('user_id'): 
        flash("You cannot delete your own admin account!", "warning")
        return redirect(url_for('manage_user.manage_users'))
    
    
    CHECK_QUERY="""SELECT id from users WHERE id=%s"""
    user=db.fetchQuery(CHECK_QUERY,(id,))
    
    if not user:
        flash('User not found', "danger")
        return redirect(url_for('manage_user.manage_users'))
    
    DELETE_QUERY="""
         DELETE FROM users WHERE id=%s
    """
    
    db.executeQuery(DELETE_QUERY,(id,))
    flash("User deleted successfully", "success")
    return redirect(url_for('manage_user.manage_users'))
    
    

# Edit
@manage_user_bp.route('/admin/manage_users/edit/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
@csrf_protected
def edit_users(id):
   
    CHECK_QUERY="SELECT * from users WHERE id=%s"
    user=db.fetchQuery(CHECK_QUERY,(id,))
        
    if not user:
            flash('User not found', "danger")
            return redirect(url_for('manage_user.manage_users'))
    
    user=user[0]
    if request.method=='POST':
        username=request.form.get('username').strip()
        email=request.form.get('email').strip()
        password=request.form.get('password')
        role=request.form.get('role').lower()
        status=request.form.get('status')
        
        if password:
            hashed_password=generate_password_hash(password)
            UPDATE_QUERY="""
                UPDATE users SET username=%s,email=%s,password=%s,role=%s,status=%s
                WHERE id=%s
            """
            values=(username,email,hashed_password,role,status,id)
            
        else:
            UPDATE_QUERY="""
                UPDATE users set username=%s,email=%s,role=%s,status=%s
                WHERE id=%s
            """
            values=(username,email,role,status,id)
            
        db.executeQuery(UPDATE_QUERY,values)
        flash('User edited successfully',"success")
        return (redirect(url_for('manage_user.manage_users')))
    
    return render_template('admin/user_management/edit-users.html',user=user)
        
    
        
    
    
      
    
   
    


        
        
    

    