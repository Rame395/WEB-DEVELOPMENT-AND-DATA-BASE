from flask import Blueprint,render_template,url_for,request,redirect,flash
from database.schema import db
import json
from datetime import datetime
from decorator import csrf_protected

search_bp=Blueprint('search',__name__)


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
    


@search_bp.route('/search', methods=['GET', 'POST'])
@csrf_protected
def search():
    if request.method == 'POST':
        city = request.form.get('city')
        room_type = request.form.get('room_type')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        guests = request.form.get('guests')
        currency_code=request.form.get('currency')
        
        
        currency_data = db.fetchQuery("""
                         SELECT exchange_rate_to_gbp,symbol FROM currencies WHERE code = %s
                         """,  (currency_code,))
        if not currency_data:
                flash("Invalid Currency", "danger")
                return redirect(url_for('search.search'))
        exchange_rate=currency_data[0]['exchange_rate_to_gbp']
        symbol = currency_data[0]['symbol']
                
         
        query = """
            SELECT
                c.name AS city_name,
                h.name AS hotel_name,
                h.id AS hotel_id,
                h.address,
                h.description,
                h.image_url,
                h.rating,
                h.base_price_peak,
                h.base_price_offpeak,
                rt.price_multiplier,
                rt.max_guests,
                rt.name AS room_type,
                rt.id AS room_type_id,
                rt.default_features,
                MIN(r.id) AS room_id
            FROM cities c
            JOIN hotels h ON h.city_id = c.id
            JOIN rooms r ON r.hotel_id = h.id
            JOIN room_types rt ON rt.id = r.room_type_id
            WHERE LOWER(rt.name) = LOWER(%s) AND rt.max_guests >= %s
        """
               
            
        
        params = [room_type, guests]
        if city != 'All Cities':
            query += " AND c.name = %s"
            params.append(city)
            
        query += " GROUP BY h.id, rt.id"
        
        data = db.fetchQuery(query, tuple(params))
        season= get_season(check_in)
        
        nights= calculate_nights(check_in, check_out)
       
        
     
    
        for hotel in data:
            if season == "peak":
                base_price = round(hotel['base_price_peak'] * hotel['price_multiplier'] * nights,2)
            else:
                base_price= round(hotel['base_price_offpeak'] * hotel['price_multiplier'] * nights,2)
                
            
            
            hotel['rooms_available'] = db.fetchQuery("""
                    SELECT COUNT(*) AS available_rooms 
                    FROM rooms r
                    WHERE r.hotel_id = %s 
                    AND r.room_type_id = %s
                    AND r.id NOT IN (
                        SELECT b.room_id 
                        FROM bookings b
                        WHERE b.status IN ('confirmed', 'pending')
                        AND (b.status != 'pending' OR b.expires_at > NOW())
                        AND b.check_in_date < %s  
                        AND b.check_out_date > %s
                    )
                """, (hotel['hotel_id'], hotel['room_type_id'], check_out, check_in))[0]['available_rooms']
            
            final_price=round(base_price/exchange_rate,2)
            hotel['final_price']=final_price
            hotel['symbol']=symbol
            hotel['season']=season
            hotel['nights']=nights
            
       
        
            if isinstance(hotel['default_features'], str):
                hotel['default_features'] = json.loads(hotel['default_features'])
                
        sort_option = request.form.get('sort', 'default')
        
        if sort_option == 'price_low':
                data.sort(key=lambda hotel: hotel['final_price']) 
                
               
        elif sort_option == 'price_high':
                data.sort(key=lambda hotel: hotel['final_price'], reverse=True) 
               
        elif sort_option == 'rating':
                data.sort(key=lambda hotel: hotel['rating'], reverse=True)
        
        # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        #     return render_template('search_result.html', hotels=data)
            
            
        return render_template('search_result.html', hotels=data,search_params=request.form,city=city,check_in=check_in,check_out=check_out)
    return render_template('search.html')
       

       
       
@search_bp.route('/search/search_result')
def search_result():
    return render_template('search_result.html')
     
            



            
                
            
            
        

        






        
        
        
        
       
    