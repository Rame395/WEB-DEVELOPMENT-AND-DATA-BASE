from flask import Blueprint,render_template,url_for,redirect,flash,request
from decorator import admin_required,login_required,csrf_protected



from database.schema import db
from database.utils import run_global_cleanup


manageRooms_bp=Blueprint('manage_room',__name__)


    
    
@manageRooms_bp.route('/admin/manage_room')
@login_required
@admin_required
@csrf_protected
def manage_rooms():
    
    run_global_cleanup()
    
    ROOMS_LIST_QUERY="""
                SELECT 
                    r.id as room_id,
                    h.name as hotel_name,
                    c.name as city_name,
                    rt.name as room_type,
                    r.room_number,
                    r.status
                FROM rooms r
                JOIN hotels h on r.hotel_id=h.id
                JOIN cities c on r.city_id=c.id
                JOIN room_types rt ON r.room_type_id=rt.id
            """
            
    all_room=db.fetchQuery(ROOMS_LIST_QUERY)
    return render_template("admin/room_management/manage_room.html", rooms=all_room)


@manageRooms_bp.route('/admin/edit-room/<int:room_id>', methods=['POST','GET'])
@login_required
@admin_required
@csrf_protected
def edit_room(room_id):
    if request.method=="POST":
        new_status = request.form.get('status').strip().lower()
        print(f"New Status: {new_status}")
    
    
        is_occupied = db.fetchQuery("""
            SELECT id FROM bookings 
            WHERE room_id = %s AND status = 'confirmed' 
            AND CURRENT_DATE >= check_in_date 
            AND CURRENT_DATE <= check_out_date
        """, (room_id,))
      
        if len(is_occupied) > 0:
          if new_status != 'booked':
            flash(f"Security Alert: Cannot change status to '{new_status}'. This room is currently occupied by a guest until their check-out date.", "danger")
            return redirect(request.url)

        
        
        db.executeQuery("""
            UPDATE rooms SET status = %s
            WHERE id = %s
        """, (new_status,  room_id))
        flash("Room updated successfully", "success")
        return redirect(url_for('manage_room.manage_rooms'))
        
        
    
    room = db.fetchQuery("SELECT * FROM rooms WHERE id = %s", (room_id,))
    if not room:
        flash("Room not found", "warning")
        return redirect(url_for('manageRooms.manage_rooms'))
    
    return render_template('admin/room_management/edit_room.html',room=room[0])

