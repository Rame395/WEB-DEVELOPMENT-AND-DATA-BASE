from flask import Blueprint,render_template,current_app,flash,redirect,url_for
from decorator import admin_required,login_required
from database.schema import db
booking_details_bp=Blueprint('booking_details',__name__)




@booking_details_bp.route('/admin/master_booking')
@login_required
@admin_required
def bookings():
    try:
        db.executeQuery("""
            UPDATE bookings 
            SET status = 'cancelled' 
            WHERE status = 'pending' 
            AND expires_at < NOW()
        """)
        

        bookings = db.fetchQuery("SELECT * FROM bookings")
        return render_template('admin/master_booking/master_booking.html', my_booking=bookings)
    
    except Exception as e:
        current_app.logger.error(f"Error fetching booking details: {e}")
        flash('An error occurred while loading your profile', 'error')
        
        
@booking_details_bp.route('/admin/booking_details/<booking_code>') 
@login_required
@admin_required
def booking_details(booking_code):
    try:
       
        results = db.fetchQuery("SELECT * FROM booking_details WHERE booking_code = %s", (booking_code,))
        
       
        if not results:
            flash('Booking not found', 'warning')
            return redirect(url_for('booking_details.bookings')) 

       
        return render_template('admin/master_booking/booking_details.html',
                           booking=results[0])
    
    except Exception as e:
        current_app.logger.error(f"Error fetching booking details: {e}")
        flash('An error occurred while loading booking details', 'error')
        return redirect(url_for('admin.master_booking'))

    
    



