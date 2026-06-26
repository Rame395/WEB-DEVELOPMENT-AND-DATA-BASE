from flask import Blueprint,render_template,url_for,redirect,flash,session,abort,request,current_app
from decorator import admin_required,login_required,csrf_protected
from werkzeug.utils import secure_filename

from database.schema import db
import os

manage_hotel_bp=Blueprint('manage_hotel',__name__)


    
        
@manage_hotel_bp.route('/admin/manage_hotels')
@login_required
@admin_required
@csrf_protected
def manage_hotels():
    Hotel_LIST_QUERY="""
        SELECT
                c.name AS city_name,
                c.capacity,
                h.name AS hotel_name,
                h.id AS hotel_id,
                h.address,
                h.description,
                h.image_url,
                h.rating,
                h.is_active AS status,
                h.base_price_peak As peak_price,
                h.base_price_offpeak AS offPeak_price,
                rt.price_multiplier,
                rt.max_guests,
                rt.name AS room_type,
                rt.id AS room_type_id,
                rt.default_features
            FROM cities c
            JOIN hotels h ON h.city_id = c.id
            JOIN rooms r ON r.hotel_id = h.id
            JOIN room_types rt ON rt.id = r.room_type_id
            group by h.id,rt.id;
    """
    
    capacity_data = db.fetchQuery("SELECT * FROM view_hotel_room_distribution")
    capacity = capacity_data[0] if capacity_data else {}
    
    hotels=db.fetchQuery(Hotel_LIST_QUERY)
    
    
    COUNT_QUERY="""
          SELECT COUNT(*) AS total FROM hotels
    """
    total_hotels = db.fetchQuery(COUNT_QUERY)[0]['total']
    
    
    
    for hotel in hotels:
        hotel['rooms_available']=db.fetchQuery("""
                    SELECT COUNT(*) AS available_rooms FROM rooms WHERE hotel_id = %s AND room_type_id = %s""", (hotel['hotel_id'], hotel['room_type_id']))
        
    
    
    return render_template(
        "admin/hotel_management/manage_hotel.html",
        hotels=hotels,
        total_hotels=total_hotels,
        capacity=capacity
    )
    



ALLOWED_EXTENSION = {'png','jpg','jpeg','gif','webp','avif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

import os
from flask import current_app

def delete_old_image(image_relative_path):
    if not image_relative_path:
        return # Nothing to delete
    
  
    absolute_path = os.path.join(current_app.static_folder, image_relative_path.replace('images/', ''))
    
    try:
        if os.path.exists(absolute_path):
            os.remove(absolute_path)
            print(f"Successfully deleted: {absolute_path}")
    except Exception as e:
        print(f"Failed to delete {absolute_path}: {e}")
 

        
        

   
     



@manage_hotel_bp.route('/admin/manage_hotel/add_hotel', methods=['POST', 'GET'])
@login_required
@admin_required
@csrf_protected
def addHotel():
    if request.method == "POST":
        city = request.form.get('city')
        hotel = request.form.get('name')
        address = request.form.get('address')
        description = request.form.get('description')
        peak_rate = request.form.get('peak_rate')
        offPeak_rate = request.form.get('offpeak_rate')
        
       
        image_db_path = "images/default_hotel.jpg" 

        hotel_exists = db.fetchQuery(
            "SELECT name FROM hotels WHERE name=%s", (hotel,)
        )
        if hotel_exists:
            flash(f"Hotel with name {hotel} already exists")
            return redirect(url_for('manage_hotel.manage_hotels'))
        
        city_data = db.fetchQuery("SELECT id FROM cities WHERE name=%s", (city,))
        if not city_data:
            flash(f"City {city} not found in database", "danger")
            return redirect(request.url)
         
        city_id = city_data[0]['id']

       
        if 'hotel_image' in request.files:
            file = request.files['hotel_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"{hotel}_{file.filename}")
                upload_folder = os.path.join(current_app.static_folder, 'images')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                image_db_path = f"images/{filename}"
          
        try:  
           
            db.executeQuery("""
                INSERT INTO hotels (city_id, name, address, description, base_price_peak, base_price_offpeak, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (city_id, hotel, address, description, peak_rate, offPeak_rate, image_db_path))
            
       
            new_hotel = db.fetchQuery("SELECT id FROM hotels WHERE name = %s ORDER BY id DESC LIMIT 1", (hotel,))
            new_id = new_hotel[0]['id']
            
         
            allocations = [
                ('Standard', 0.30, 'ST'),
                ('Double', 0.50, 'DB'),
                ('Family', 0.20, 'FM')
            ]
            
            for rt_name, percent, code in allocations:
                db.executeQuery(f"""
                    INSERT INTO rooms (hotel_id, room_type_id, city_id, room_number, features)
                    SELECT h.id, rt.id, c.id, 
                        CONCAT('H', h.id, '-{code}-', n.n), 
                        rt.default_features
                    FROM hotels h
                    JOIN cities c ON h.city_id = c.id
                    JOIN room_types rt ON rt.name = %s
                    JOIN numbers n ON n.n <= ROUND(c.capacity * %s)
                    WHERE h.id = %s
                """, (rt_name, percent, new_id))
                
            flash('Hotel and Inventory added successfully', 'success')
            return redirect(url_for('manage_hotel.manage_hotels'))
        
        except Exception as e:
            print(f"Database Error: {e}")
            flash("Error while adding hotel and capacity")
            
    return render_template('admin/hotel_management/add_hotel.html')
                
                
                
               
            
            
           

          


   
@manage_hotel_bp.route('/admin/manage_hotel/edit/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
@csrf_protected
def edit_hotel(id):
    CHECK_QUERY="SELECT * from hotels WHERE id=%s"
    hotel=db.fetchQuery(CHECK_QUERY,(id,))
    print(f"Image: {hotel}")
        
    if not hotel :
            flash('hotel not found', "danger")
            return redirect(request.url)
    
    hotel=hotel[0]
    if request.method=='POST':
        
        hotel_name=request.form.get('name')
        address=request.form.get('address')
        description=request.form.get('description')
        peak_rate=request.form.get('peak_rate')
        offPeak_rate=request.form.get('offpeak_rate')
        file = request.files.get('hotel_image')
        status=request.form.get('status')
        
        


        image_path = hotel['image_url'] 
        if file and file.filename and allowed_file(file.filename):
           
            if hotel['image_url']:
               
                old_file_path = os.path.join(current_app.static_folder, hotel['image_url'])
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

          
            filename = secure_filename(f"{id}_{file.filename}")
            upload_dir = os.path.join(current_app.static_folder, 'images')
            os.makedirs(upload_dir, exist_ok=True)
            
            file.save(os.path.join(upload_dir, filename))
            image_path = f"images/{filename}"
            

        
       
        UPDATE_QUERY="""
                UPDATE hotels SET name=%s,address=%s,description=%s,base_price_peak=%s,base_price_offpeak=%s,image_url=%s,is_active=%s
                WHERE id=%s
            """
        values=(hotel_name,address,description,peak_rate,offPeak_rate,image_path,status,id)
            
       
        db.executeQuery(UPDATE_QUERY,values)
        flash('Hotel edited successfully',"success")
        return redirect(request.url)
    
    return render_template('admin/hotel_management/edit_hotel.html',hotel=hotel)
            
                           


@manage_hotel_bp.route('/admin/manage_hotel/remove/<int:id>')
@login_required
@admin_required
def removeHotel(id):
    CHECK_QUERY="""SELECT id from hotels WHERE id=%s"""
    hotel=db.fetchQuery(CHECK_QUERY,(id,))
    
    if not hotel:
        flash('hotel not found', "danger")
        return redirect(url_for('manage_hotel.manage_hotels'))
    
    DELETE_QUERY="""
         DELETE FROM hotels WHERE id=%s
    """
    
    db.executeQuery(DELETE_QUERY,(id,))
    flash("hotel deleted successfully", "success")
    return redirect(url_for('manage_hotel.manage_hotels'))
        
    