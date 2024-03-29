import os
from config import Config
from models import db, ChargingStationBooking
from flask import Flask, request, jsonify, Blueprint
from models import ChargingStation, ChargingStationBooking, db
from sqlalchemy import text, func
from datetime import datetime, timedelta
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config.from_object(Config)
#initializes the database with the flask application context to bind the flask app with SQLAlchemy database instance
db.init_app(app)
scheduler = APScheduler()


#Functionalities: 
# 1. HTTP post: Notify booking ends in 15mins
# 2. HTTP PUT 1. Report late collection base on the {booking_id}


def check_bookings_to_notify():
    now = datetime.now()
    upcoming_end_time = now + timedelta(minutes=15)
    # Query for bookings ending within the next 15 minutes
    bookings = ChargingStationBooking.query.filter(
        ChargingStationBooking.booking_datetime + timedelta(hours=ChargingStationBooking.booking_duration_hours) <= upcoming_end_time,
        ChargingStationBooking.booking_status == 'IN_PROGRESS'
    ).all()
    
    for booking in bookings:
        send_notification(booking.user_id, f"Your booking ends in 15 minutes.")


def send_notification(user_id, message):
    # Placeholder for notification logic
    # integrate with an email service/ SMS gateway or another notification service to send the nofication to the user 
    print(f"Notification for user {user_id}: {message}")
    
    
def check_and_update_bookings():
    with app.app_context():
        # Current time
        now = datetime.now()
        # Query all bookings that should now be marked as EXCEEDED
        bookings_to_update = ChargingStationBooking.query.filter(
            ChargingStationBooking.booking_datetime + timedelta(hours=ChargingStationBooking.booking_duration_hours) < now,
            ChargingStationBooking.booking_status != 'EXCEEDED'  # Only update if status is not already EXCEEDED
        ).all()

        for booking in bookings_to_update:
            booking.booking_status = 'EXCEEDED'
            db.session.commit()
        print(f"Updated {len(bookings_to_update)} booking(s) to EXCEEDED.")
        
def initialize_scheduler():
    scheduler.init_app(app)
    scheduler.start()
    # Run the job every 10 minutes
    scheduler.add_job(id='Scheduled Booking Checker', func=check_and_update_bookings, trigger='interval', minutes=10)

with app.app_context():
    initialize_scheduler()

#determines the root path of application so that Flask can find resource files relative to the location of application
if __name__ == '__main__': 
    print("This is flask for " + os.path.basename(__file__) + ": managing charger availability microservice ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
#setting the microservice to run on port 5002 (need to check if theres any conflicts with other services) 