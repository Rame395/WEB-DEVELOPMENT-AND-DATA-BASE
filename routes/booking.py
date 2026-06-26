from flask import Blueprint,render_template,url_for,redirect,flash,session,request,abort
import random
import string
from datetime import datetime,timedelta
import json
from decimal import Decimal
from database.schema import db
from database.utils import run_global_cleanup
from decorator import login_required,csrf_protected
from decorator import login_required





booking_bp=Blueprint('booking',__name__)


def generate_booking_code():
    return "BK-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def get_season(check_in_date):
    month = datetime.strptime(check_in_date, "%Y-%m-%d").month

    if 4 <= month <= 8 or month in (11, 12):
        return "peak"
    return "off_peak"

def calculate_nights(check_in, check_out):
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
    check_out_date = datetime.strptime(check_out, "%Y-%m-%d")

    nights = (check_out_date - check_in_date).days
    return nights

from datetime import datetime

   
   
def calculate_advance(check_in):
    check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
    
    today = datetime.today().date()

    days_advance = (check_in_date - today).days
  
    return max(0, days_advance)





   
def validate_booking(check_in_str, check_out_str):
    try:
        today = datetime.now().date()
        check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
        
       
        if check_in < today:
            return "Check-in date cannot be in the past.", "danger"
            
       
        duration = (check_out - check_in).days
        if duration <= 0:
            return "Check-out must be at least one day after check-in.", "danger"
            
      
        if duration > 30:
            return "Stay exceeds the 30-day limit. Please make separate bookings for longer durations.", "danger"
        
        return None,None
        
    except ValueError:
        return "Invalid date format. Please try again.", "danger"





    
    
    
def get_price_breakdown(room_id, check_in, check_out, currency_code):
    total_nights = calculate_nights(check_in, check_out)
    days_advance = calculate_advance(check_in)
    
    room_datas = db.fetchQuery("""
         SELECT
            h.base_price_peak, h.base_price_offpeak, rt.price_multiplier
         FROM hotels h
         INNER JOIN rooms r ON r.hotel_id = h.id
         INNER JOIN room_types rt ON rt.id = r.room_type_id
         WHERE r.id=%s
    """, (room_id,))
    
    if not room_datas:
        raise ValueError("Data not found.")
    room_data=room_datas[0] 
   
        
    
    currency = db.fetchQuery("SELECT exchange_rate_to_gbp, symbol FROM currencies WHERE code = %s", (currency_code,))
    if not currency:
        raise ValueError("Data not found.")
    currency_data=currency[0]
    
    
   
    exchange_rate = Decimal(str(currency_data['exchange_rate_to_gbp']))
    if exchange_rate <= 0:
      exchange_rate = Decimal('1.00')
    multiplier = Decimal(str(room_data['price_multiplier']))
    
    season = get_season(check_in)
    raw_base_price = room_data['base_price_peak'] if season == 'peak' else room_data['base_price_offpeak']
    price_per_night_gbp = Decimal(str(raw_base_price))

  
    per_night = ((price_per_night_gbp *multiplier)/ exchange_rate).quantize(Decimal('0.01'))
    
  
    base_stay_price_converted = (price_per_night_gbp * multiplier * total_nights) / exchange_rate
    base_price = base_stay_price_converted.quantize(Decimal('0.01'))
    
   
    discount_rate = Decimal('0.00')
    if 80 <= days_advance <= 90: discount_rate = Decimal('0.30')
    elif 60 <= days_advance <= 79: discount_rate = Decimal('0.20')
    elif 45 <= days_advance <= 59: discount_rate = Decimal('0.10')
    
    discount_amount = (base_price * discount_rate).quantize(Decimal('0.01'))
    final_price = base_price - discount_amount
    
    return {
        "total_nights": total_nights,
        "price_per_night": float(per_night),
        "base_price": float(base_price),
        "discount_amount": float(discount_amount),
        "discount_rate": float(discount_rate),
        "final_price": "{:.2f}".format(final_price), # Formats to 2 decimal places as a string
        "symbol": currency_data['symbol'],
        "exchange_rate": float(exchange_rate),
        "season": season
}
    
     
def create_booking(user_id,room_id ,hotel_id,room_type_id, check_in, check_out, guests, currency_code):
    error_msg, category = validate_booking(check_in, check_out)
    
    if error_msg:
        return False, error_msg
        
    # print(f"Category: {category}")

    try:
        db.begin()
        available_room = db.fetchQuery("""
                    SELECT id FROM rooms 
                    WHERE hotel_id = %s AND room_type_id = %s
                    AND id NOT IN (
                        SELECT room_id FROM bookings 
                        WHERE (status = 'confirmed' OR (status = 'pending' AND expires_at > NOW()))
                        AND check_in_date < %s 
                        AND check_out_date > %s
                    ) LIMIT 1 FOR UPDATE
                """, (hotel_id, room_type_id, check_out, check_in))
        
        if not available_room:
            return False, "This room was just grabbed by someone else! Please search again."
        
        final_room_id = available_room[0]['id']
        try:
            pricing = get_price_breakdown(final_room_id, check_in, check_out, currency_code)
        except Exception as e:
            return False, f"Pricing error: {str(e)}"

        expires_at = datetime.now() + timedelta(minutes=15)
        booking_code = generate_booking_code()
        
        db.executeTransaction("""
            INSERT INTO bookings(
                booking_code, user_id, room_id,
                check_in_date, check_out_date, number_of_guests, total_nights,
                base_price, discount_percentage, discount_amount,
                total_price, currency, exchange_rate, status, payment_status, expires_at)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', 'pending', %s)
        """, (
            booking_code, user_id, final_room_id, 
            check_in, check_out, guests, pricing['total_nights'],
            pricing['base_price'], pricing['discount_rate'], pricing['discount_amount'],
            pricing['final_price'], currency_code, pricing['exchange_rate'], expires_at
        ))
        db.commit()
        return True, booking_code

    except Exception as e:
        db.rollback()
        print(f"Booking Error: {e}")
        return False, str(e)
       
                    

                    
                    
@booking_bp.route('/booking', methods=['POST', 'GET'])
@login_required
@csrf_protected
def book_room():


    if request.method == 'GET':
        room_id = request.args.get('room_id')
        hotel_id = request.args.get('hotel_id')
        room_type_id = request.args.get('room_type_id')

        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        guests = request.args.get('guests')
        currency = request.args.get('currency') or request.form.get('currency') or 'GBP'

        if not all([room_id, check_in, check_out, currency]):
            flash("Missing booking data. Please search again.", "danger")
            return redirect(url_for('search.search'))

        room_info = db.fetchQuery("""
            SELECT h.name AS hotel_name, h.address, h.description, h.image_url, c.name AS city_name,
                   rt.name AS room_type, rt.default_features
            FROM rooms r
            JOIN hotels h ON r.hotel_id = h.id
            JOIN cities c ON h.city_id=c.id
            JOIN room_types rt ON r.room_type_id = rt.id
            WHERE r.id = %s
        """, (room_id,))

        if not room_info:
            flash("Room not found", "danger")
            return redirect(url_for('search.search'))

        for row in room_info:
            if isinstance(row['default_features'], str):
                row['default_features'] = json.loads(row['default_features'])

        search_params = {
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'currency': currency,
            'room_id': room_id,
            'hotel_id': hotel_id,
            'room_type_id': room_type_id
        }

        pricing = get_price_breakdown(room_id, check_in, check_out, currency)
        print(f"Room Info: {room_info}")

        return render_template(
            'booking/book_room.html',
            room=room_info[0],
            search=search_params,
            pricing=pricing
        )


    print(f"Data received: {request.form.to_dict()}")

    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    guests_raw = request.form.get('guests')

    try:
        guests_count = int(guests_raw.split()[0])
    except (ValueError, AttributeError):
        guests_count = 1

    currency = request.form.get('currency')

    room_id = request.form.get('room_id')
    hotel_id = request.form.get('hotel_id')
    room_type_id = request.form.get('room_type_id')

    success, result = create_booking(
        session['user_id'],
        room_id,
        hotel_id,
        room_type_id,
        check_in,
        check_out,
        guests_count,
        currency
    )

    if success:
        flash(f"Success! Booking Code: {result}", "success")
        return redirect(url_for('payment.payment', booking_code=result))
    else:
        flash(f"Error: {result}", "danger")
        return redirect(request.referrer)

    

  



    
@booking_bp.route('/my_booking')
@login_required
def my_booking():
    # db.executeQuery("""
    #     UPDATE bookings 
    #     SET status = 'cancelled' 
    #     WHERE status = 'pending' 
    #     AND expires_at < NOW()
    # """)
    
    
    run_global_cleanup()
      
    BOOKING_LIST_QUERY = """
        SELECT * FROM bookings 
        WHERE user_id = %s AND status IN ('pending', 'confirmed')
    """
       
    my_booking=db.fetchQuery(BOOKING_LIST_QUERY,(session['user_id'],))
    # print(f"My Booking :{my_booking}")
    return render_template('booking/My_booking.html',my_booking=my_booking)
        
        
    
      
    



@booking_bp.route('/booking_history')
@login_required
def booking_history():
    run_global_cleanup()
    user_id=session.get('user_id')
    history_bookings = db.fetchQuery("""
        SELECT * FROM bookings 
        WHERE user_id = %s AND status IN ('cancelled', 'completed', 'failed')
        ORDER BY booking_date DESC
    """, (user_id,))
    
    return render_template('booking/booking_history.html', 
                           history_bookings=history_bookings)
                           







def get_cancellation_fee(booking_id):
    rows = db.fetchQuery("SELECT * FROM bookings WHERE id = %s", (booking_id,))
    
    if not rows:
       raise ValueError("Booking not found.")
    booking = rows[0]
    
    today = datetime.now().date()
    check_in = booking['check_in_date']
    days_until_checkin = (check_in - today).days

   
    if days_until_checkin < 0:
        fee_percent = 1.00 
    else:
       
        policy = db.fetchQuery("""
            SELECT fee_percentage FROM cancellation_policies 
            WHERE %s BETWEEN min_days AND max_days
        """, (days_until_checkin,))

        if not policy:
            
            fee_percent = 0.00 if days_until_checkin > 999 else 1.00
        else:
            fee_percent = float(policy[0]['fee_percentage']) / 100

    total_price = float(booking['total_price'])
    fee_amount = total_price * fee_percent
    refund_amount = total_price - fee_amount

    return fee_amount, refund_amount, days_until_checkin


@booking_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
@csrf_protected
def cancel_booking(booking_id):
    booking = db.fetchQuery("""
                SELECT * FROM bookings WHERE id = %s AND user_id = %s
            """, (booking_id, session['user_id']))

    if not booking:
        abort(403)
       
    try:
        db.begin()
        fee, refund, days = get_cancellation_fee(booking_id)
        db.executeTransaction("UPDATE rooms r JOIN bookings b ON r.id = b.room_id SET r.status = 'available' WHERE b.id = %s", (booking_id,))
       
        db.executeTransaction("""
            UPDATE bookings 
            SET status = 'cancelled', cancellation_fee = %s, refund_amount = %s 
            WHERE id = %s
        """, (fee, refund, booking_id))
        flash(f"Booking cancelled. Days notice: {days}. Fee: {fee}. Refund: {refund}", "success")
        db.commit()
        
    except Exception as e:
        flash(f"Error processing cancellation: {str(e)}", "danger")
        db.rollback()
        
    return redirect(url_for('booking.my_booking'))



       
@booking_bp.route('/get-cancellation-details/<int:booking_id>')
@login_required
def get_details(booking_id):
    booking = db.fetchQuery("""
                SELECT * FROM bookings WHERE id = %s AND user_id = %s
            """, (booking_id, session['user_id']))

    if not booking:
        abort(403)
    try:
        fee, refund, days = get_cancellation_fee(booking_id)
        
       
        return {
            "fee": float(fee),
            "refund": float(refund),
            "days": int(days)
        }, 200
    except Exception as e:
        return {"error": str(e)}, 400



@booking_bp.route('/booking/receipt/<booking_code>')
@login_required
def view_receipt(booking_code):
    
    booking = db.fetchQuery("SELECT * FROM bookings WHERE booking_code = %s", (booking_code,))[0]
    
    if booking['user_id'] != session['user_id'] and session.get('role') != 'admin':
        return redirect(url_for('public.home'))
    
    room = db.fetchQuery("SELECT * FROM rooms WHERE id = %s", (booking['room_id'],))[0]
    hotel = db.fetchQuery("SELECT * FROM hotels WHERE id = %s", (room['hotel_id'],))[0]
    user_profile = db.fetchQuery("SELECT * FROM user_profile WHERE user_id = %s", (booking['user_id'],))[0]
    user = db.fetchQuery("SELECT email FROM users WHERE id = %s", (booking['user_id'],))[0]
    
        
    return render_template('booking/receipt.html', 
                           booking=booking, 
                           room=room, 
                           hotel=hotel, 
                           user_profile=user_profile, 
                           user=user)










    
    






    





         



        
         
    
    
    
                             
                             
    

    
    