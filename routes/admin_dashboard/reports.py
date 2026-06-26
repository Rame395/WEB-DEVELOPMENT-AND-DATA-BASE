from flask import Blueprint, render_template, request
from database.schema import db
from decorator import admin_required
from datetime import datetime, timedelta

report_bp = Blueprint('reports', __name__)

@report_bp.route('/admin/statistics')
@admin_required
def report():
  
    start = request.args.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))

   
    summary_query = db.fetchQuery("SELECT * FROM view_admin_summary")
    summary = summary_query[0] if summary_query else {}
    
 
    top_customers_query = db.fetchQuery('SELECT * FROM view_top_customers')
    top_customers = top_customers_query[0] if top_customers_query else {}

   
    sales = db.fetchQuery("""
        SELECT 
            DATE_FORMAT(b.booking_date, '%b %d') as label, 
            SUM(b.total_price * c.exchange_rate_to_gbp) as revenue 
        FROM bookings b
        JOIN currencies c ON b.currency = c.code
        WHERE b.payment_status='paid' AND b.booking_date BETWEEN %s AND %s
        GROUP BY label 
        ORDER BY MIN(b.booking_date) ASC 
    """, (start, end))

   
    hotels = db.fetchQuery("SELECT * FROM view_hotel_performance")

   
    customers = db.fetchQuery("""
        SELECT 
            u.username, 
            u.email, 
            up.fullname,
            SUM(b.total_price * c.exchange_rate_to_gbp) as spend
        FROM users u 
        JOIN user_profile up ON u.id = up.user_id
        JOIN bookings b ON u.id = b.user_id 
        JOIN currencies c ON b.currency = c.code
        WHERE b.payment_status = 'paid'
        GROUP BY u.id, u.username, u.email, up.fullname
        ORDER BY spend DESC 
        LIMIT 5
    """)
    
    
    loyalty_level = db.fetchQuery("""

        SELECT * FROM customer_analytics ORDER BY total_spend DESC LIMIT 5
    """)
    
    

   
    total_rooms = summary.get('total_rooms', 0)
    booked_rooms = summary.get('booked_rooms', 0)
    occ_rate = (booked_rooms / total_rooms * 100) if total_rooms > 0 else 0

    return render_template('admin/reports_analytics.html', 
        start=start, 
        end=end,
        revenue=summary.get('total_revenue', 0), 
        counts={
            'confirmed': summary.get('confirmed_bookings', 0),
            'pending': summary.get('pending_bookings', 0),
            'completed': summary.get('completed_bookings', 0),
            'cancelled': summary.get('cancelled_bookings', 0)
        },
        rooms={
            'available': summary.get('available_rooms', 0),
            'booked': summary.get('booked_rooms', 0),
            'maintenance': summary.get('maintenance_rooms', 0)
        },
        occupancy_rate=round(occ_rate, 1),
        sales=sales, 
        hotels=hotels, 
        customers=customers, 
        top_customer=top_customers,
        loyalty_level=loyalty_level
        
        
    )