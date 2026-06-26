from database.schema import db
from datetime import datetime

def run_global_cleanup():
    now = datetime.now()
    today = now.date()

    try:
        db.begin()
       
        db.executeTransaction("UPDATE bookings SET status = 'cancelled' WHERE status = 'pending' AND expires_at < %s", (now,))

       
        db.executeTransaction("UPDATE bookings SET status = 'completed' WHERE status = 'confirmed' AND check_out_date <= %s", (today,))

       
        db.executeTransaction("""
            UPDATE rooms r
            JOIN bookings b ON r.id = b.room_id
            SET r.status = 'booked'
            WHERE b.status = 'confirmed'
            AND %s >= b.check_in_date AND %s < b.check_out_date
        """, (today, today))

       
        db.executeTransaction("""
            UPDATE rooms r
            SET r.status = 'available'
            WHERE r.status = 'booked'
            AND r.id NOT IN (
                SELECT room_id FROM bookings 
                WHERE status = 'confirmed'
                AND %s >= check_in_date AND %s < check_out_date
            )
        """, (today, today))

       
        db.commit() 
        print("Cleanup successful.")
    except Exception as e:
        db.rollback()
        print(f"Cleanup failed: {e}")