from flask import Blueprint,render_template
from decorator import admin_required,login_required



adminPanel_bp=Blueprint("adminPanel",__name__)

@login_required
@admin_required
@adminPanel_bp.route('/admin/adminPanel')
def admin_panel():
    return render_template('admin/admin_base.html')


   
