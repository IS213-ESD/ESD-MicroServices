from flask import Flask, request, jsonify, Blueprint, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import  datetime, timedelta, timezone
import logging
from invokes import invoke_http
# from apscheduler.executors.pool import ThreadPoolExecutor
import pika
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

# executors = {
#     'default': ThreadPoolExecutor(30)  # Adjust the number of threads based on your needs
# }
# scheduler = BackgroundScheduler(executors=executors)
# scheduler = BackgroundScheduler()

app = Flask(__name__)

RABBITMQHOST = os.getenv('RABBITMQHOST')
booking_URL = os.getenv('BOOKING_URL')
COMPLEX_HANDLE_LATE_COLLECTION_BASE = os.getenv('COMPLEX_HANDLE_LATE_COLLECTION_BASE')
CHARGING_STATION_BOOKING_BASE = os.getenv('CHARGING_STATION_BOOKING_BASE')

def connect_to_rabbitmq():
    attempts = 0
    while True:
        try:
            print(f"Trying to connect to RabbitMQ (attempt {attempts + 1})")
            parameters = pika.ConnectionParameters(RABBITMQHOST)
            connection = pika.BlockingConnection(parameters)
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            attempts += 1
            print(f"Failed to connect to RabbitMQ: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

def send_notification(queue_name, message):
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(f"Sent notification to {queue_name}: {message}")

@app.teardown_appcontext
def close_rabbitmq_connection(exception=None):
    connection.close()
    print("RabbitMQ connection closed")

def check_database():
    logging.info(f"Checking database at {datetime.now()}")
    booking_result = invoke_http(booking_URL, method="GET")
    current_time = datetime.now()
    # current_time = datetime(2024, 3, 31, 15, 45, 0, tzinfo=timezone.utc)
    for booking in booking_result["bookings"]:
        booking_datetime = datetime.strptime(booking["booking_datetime"], "%a, %d %b %Y %H:%M:%S %Z")
        # booking_datetime = booking_datetime.replace(tzinfo=timezone.utc)  # Make it offset-aware 
        booking_status = booking.get('booking_status')
        user_id = booking.get('user_id')
        end_time = booking_datetime + timedelta(hours=booking["booking_duration_hours"])
        booking_id = booking.get('booking_id')
        notification_after = booking.get('notification_after')
        notification_before = booking.get('notification_before')
        # print(f"{booking_id} {booking_datetime} {current_time} {notification_after} {notification_before}")
        # flow for bookings ending in 15 mins 
        if current_time <= end_time <= current_time + timedelta(minutes=15) and booking_status == "IN_PROGRESS" and notification_after is False:
            message = {'msg': 'Booking ends in 15 minutes, Please be ready to vacate the lot', 'user_id': user_id}
            json_message = json.dumps(message)
            print(json_message)
            invoke_http(CHARGING_STATION_BOOKING_BASE + f"/update_notification_after/{booking_id}", method='POST')
            notification_result = send_notification('user_sms_notifications', json_message)
            logging.info(f"Booking ID {booking_id} ENDING SOON - {notification_result}")
            
        # flow for bookings that have exceeded time 
        elif end_time < current_time and booking_status == "IN_PROGRESS":
            message = {'msg': 'Your booking has exceeded its allotted time. Late charges will apply. Please vacate the lot as soon as possible. Thank you.', 'user_id': user_id}
            json_message = json.dumps(message)
            print(json_message)
            # notification_result = send_notification('user_sms_notifications', json_message)
            # needs to be updated with the new url for exceed bookings******
            exceed_result = invoke_http(COMPLEX_HANDLE_LATE_COLLECTION_BASE + "/handle_late_collection", method='PUT', json={'booking_id':booking_id})
            print(exceed_result, booking_id)
            # logging.info(f"Booking ID {booking_id} EXCEEDED - {notification_result}")
            
        # flow to start bookings
        elif current_time <= booking_datetime <= current_time + timedelta(minutes=15) and booking_status == "IN_PROGRESS" and notification_before is False:
            message = {'msg': 'Your booking will start in 15 minutes!', 'user_id': user_id}
            json_message = json.dumps(message)
            print(json_message)
            invoke_http(CHARGING_STATION_BOOKING_BASE + f"/update_notification_before/{booking_id}", method='POST')
            notification_result = send_notification('user_sms_notifications', json_message)
            logging.info(f"Booking ID {booking_id} UPCOMING - {notification_result}")
            
    logging.info("ONE CYCLE DONE")

connection = connect_to_rabbitmq()
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_database, trigger="interval", seconds=10)
# scheduler.add_job(check_database, 'cron', minute='*/15')
scheduler.start()

@app.route('/')
def home():
    return jsonify({'status': "Up and running"}), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5006, debug=True)
