from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import  datetime, timedelta, timezone
import logging
from invokes import invoke_http
from apscheduler.executors.pool import ThreadPoolExecutor

# executors = {
#     'default': ThreadPoolExecutor(30)  # Adjust the number of threads based on your needs
# }
# scheduler = BackgroundScheduler(executors=executors)
# scheduler = BackgroundScheduler()
booking_URL = "http://delectric-charging-station:5001/charging-station-booking/"
exceed_URL = "http://delectric-charging-station:5001/charging-station-booking/exceed_booking"
notification_URL = "http://delectric-manage-notifications:5103/send-notification"

app = Flask(__name__)

def check_database():
    logging.info(f"Checking database at {datetime.now()}")
    booking_result = invoke_http(booking_URL, method="GET")
    # current_time = datetime.now(timezone.utc)
    current_time = datetime(2024, 3, 31, 15, 45, 0, tzinfo=timezone.utc)

    for booking in booking_result["bookings"]:
        booking_datetime = datetime.strptime(booking["booking_datetime"], "%a, %d %b %Y %H:%M:%S %Z")
        booking_datetime = booking_datetime.replace(tzinfo=timezone.utc)  # Make it offset-aware
        booking_status = booking.get('booking_status')
        user_id = booking.get('user_id')
        end_time = booking_datetime + timedelta(hours=booking["booking_duration_hours"])
        booking_id = booking.get('booking_id')

        # flow for bookings ending in 15 mins 
        if current_time <= end_time <= current_time + timedelta(minutes=15) and booking_status == "IN_PROGRESS":
            notification_result = invoke_http(notification_URL, method='POST', json={'msg':"Booking ends in 15 minutes, Please be ready to vacate the lot",'user_id':user_id})
            logging.info(f"Booking ID {booking_id} ENDING SOON - {notification_result}")
            

        # flow for bookings that have exceeded time 
        elif end_time < current_time and booking_status == "IN_PROGRESS":
            logging.info(f"Booking ID {booking_id} EXCEEDED - ")
            # needs to be updated with the new url for exceed bookings******
            
            # exceed_result = invoke_http(exceed_URL, method='POST', json={'booking_id':booking_id})
            # logging.info(booking_id,"found for exceeded",exceed_result)
            

        # flow to start bookings
        elif current_time <= booking_datetime <= current_time + timedelta(minutes=15) and booking_status == "IN_PROGRESS":
            notification_result = invoke_http(notification_URL, method='POST', json={'msg':"Booking starts in 15 minutes!",'user_id':user_id})
            logging.info(f"Booking ID {booking_id} UPCOMING - {notification_result}")
            

    logging.info("ONE CYCLE DONE")

scheduler = BackgroundScheduler()
# scheduler.add_job(func=check_database, trigger="interval", seconds=10)
scheduler.add_job(check_database, 'cron', minute='*/15')
scheduler.start()

@app.route('/')
def home():
    return "Charger-Availability is running!"

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5006, debug=False)
