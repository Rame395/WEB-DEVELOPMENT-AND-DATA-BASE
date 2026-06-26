from flask import Blueprint,render_template,url_for,session,redirect
from decorator import admin_required,login_required


dashboard_bp=Blueprint("dashboard",__name__)
   
@dashboard_bp.route("/admin/dashboard")
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')
   


@dashboard_bp.route('/user/dashboard')
@login_required
def user_dashboard():
    if session.get('role') == 'admin':
        return redirect(url_for('dashboard.admin_dashboard'))
    return render_template('users/user_dashboard.html')
    
        
        
    



    


    
  