from flask import Blueprint,render_template,redirect,url_for,flash,session,current_app
from flask_mail import Message
from database.schema import db
from app import mail
import uuid

payment_bp=Blueprint('payment',__name__)

@payment_bp.route('/payment/<booking_code>')
def payment(booking_code):
    BOOKING_QUERY="""
         SELECT * FROM bookings
         WHERE booking_code=%s AND payment_status='pending'
    """
    booking=db.fetchQuery(BOOKING_QUERY,(booking_code,))
    
    if not booking:
        flash("Invalid or already paid booking", "danger")
        return redirect(url_for('booking.book_room'))
    
    expiry_iso = booking[0]['expires_at'].isoformat() if booking[0]['expires_at'] else ""
    return render_template(
        "payment/payment.html",
        booking=booking[0],
        booking_code=booking_code,
        expiry_time=expiry_iso
    )
    

@payment_bp.route('/payment/success/<booking_code>')
def payment_success(booking_code):
    booking = db.fetchQuery("""
        SELECT *
        FROM bookings
        WHERE booking_code=%s
        AND status='pending'
        AND payment_status='pending'
        AND expires_at > NOW()
    """, (booking_code,))

    if not booking:
        flash("Payment expired or invalid booking", "danger")
        return redirect(url_for('booking.my_booking'))

    booking = booking[0]
    transaction_id = str(uuid.uuid4())

        

    try:
        db.begin()
        db.executeTransaction("""
            INSERT INTO payments (
                booking_id,
                payment_method,
                amount,
                currency,
                status,
                transaction_id
            )
            VALUES (%s,%s,%s,%s,'success',%s)
        """, (
            booking['id'],
            'dummy',
            booking['total_price'],
            booking['currency'],
            transaction_id
        ))

        db.executeTransaction("""
            UPDATE bookings
            SET payment_status='paid',
                status='confirmed'
            WHERE id=%s
            AND payment_status='pending'
        """, (booking['id'],))
        
        
        db.executeTransaction("""
            UPDATE rooms 
            SET status = 'booked'
            WHERE id = %s
        """, (booking['room_id'],))

        db.commit()  
      


    except Exception as e:
        db.rollback()
        print(f"PAYMENT DATABASE ERROR: {e}") 
        flash(f"Payment failed: {str(e)}", "danger")
        return redirect(url_for('payment.payment', booking_code=booking_code))
    
    room = db.fetchQuery("SELECT * FROM rooms WHERE id = %s", (booking['room_id'],))[0]
    hotel = db.fetchQuery("SELECT * FROM hotels WHERE id = %s", (room['hotel_id'],))[0]
    user_profile = db.fetchQuery("SELECT * FROM user_profile WHERE user_id = %s", (booking['user_id'],))[0]
    user = db.fetchQuery("SELECT email FROM users WHERE id = %s", (booking['user_id'],))[0]
    
    email_body= render_template('booking/receipt_email.html', 
                           booking=booking, 
                           room=room, 
                           hotel=hotel, 
                           user_profile=user_profile, 
                           user=user)
    
    try:
        user_email=session.get('email')
        msg = Message(
        subject=f"Booking Confirmed: #{booking_code}",
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user_email])
        
        msg.html = email_body
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Email failed: {e}")

    flash("Payment Successful! Booking Confirmed.", "success")
    return redirect(url_for('booking.my_booking'))


