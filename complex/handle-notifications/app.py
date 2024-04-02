import os
from os import environ
import pika
import requests
import json

from dotenv import load_dotenv

load_dotenv()


RABBITMQHOST = os.getenv('RABBITMQHOST')
USER_BASE = os.getenv('USER_BASE')
USER_NOTIFICATION_BASE = os.getenv("USER_NOTIFICATION_BASE")
CHARGING_STATION_BOOKING_BASE = os.getenv("CHARGING_STATION_BOOKING_BASE")
CHARGING_STATION_BASE = os.getenv("CHARGING_STATION_BASE")

# ROUTES
GET_BOOKING_BY_ID_URL = CHARGING_STATION_BOOKING_BASE + "/booking/"
GET_CHARGER_BY_ID_URL = CHARGING_STATION_BASE + "/chargers/"
SEND_USER_NOTIFICATION_URL = USER_NOTIFICATION_BASE + "/sendnotification"

def send_user_notification(msg, phone):
    try:
        # Craft the request payload
        payload = {
            "msg": msg,
            "phone": phone
        }
        
        # Send the notification to the user
        response = requests.post(SEND_USER_NOTIFICATION_URL, json=payload)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        
        print("Notification sent successfully")
    except requests.exceptions.RequestException as e:
        print("Failed to send notification:", e)


def get_booking_details(booking_id):
    try:
        # Construct the URL to get booking details by ID
        url = GET_BOOKING_BY_ID_URL + str(booking_id)
        
        # Retrieve booking details
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        
        booking_data = response.json()
        # Extract relevant booking details
        location = booking_data.get('location')
        date = booking_data.get('booking_datetime')
        duration = booking_data.get('booking_duration_hours')
        payment = booking_data.get('booking_fee')
        # Charger Info
        charger_id = booking_data.get('charger_id')
        charger_by_id_url = GET_CHARGER_BY_ID_URL + str(charger_id)
        charger_station_response = requests.get(charger_by_id_url)
        charger_station_response.raise_for_status()
        charger_data = charger_station_response.json()
        charger_location = charger_data.get('charger_location')
        charger_name =  charger_data.get('charger_name')

        # Craft the message
        message = f"Charger Name: {charger_name}\nCharger Location: {charger_location}\nBooking Location: {location}\nDate: {date}\nDuration: {duration} hours\nPayment: {payment}"
        return message
    except requests.exceptions.RequestException as e:
        print("Failed to retrieve booking details:", e)
        return None
    

# def send_notification(queue_name, message):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     channel = connection.channel()
#     channel.queue_declare(queue=queue_name)
#     channel.basic_publish(exchange='', routing_key=queue_name, body=message)
#     print(f"Sent notification to {queue_name}: {message}")
#     connection.close()

def booking_confirmation_callback(ch, method, properties, body):
    print("Received booking confirmation notification:", body)
    # Decode the body from bytes to string
    body_str = body.decode('utf-8')
    
    # Parse the JSON string into a Python dictionary
    request_data = json.loads(body_str)
    booking_id = request_data.get('booking_id')
    user_id = request_data.get("user_id")
    
    # Retrieve booking details
    booking_details = get_booking_details(booking_id)
    
    if booking_details:
        # Send notification to the user
        send_user_notification(booking_details, "83217652")
    else:
        print("Failed to retrieve booking details")

def car_ready_callback(ch, method, properties, body):
    print("Received car ready notification:", body)

def car_collected_callback(ch, method, properties, body):
    print("Received car collected notification:", body)

def booking_cancellation_callback(ch, method, properties, body):
    print("Received booking cancellation notification:", body)

def main():
    print("Running Handle Notifications")
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(RABBITMQHOST)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Scenario 1: Booking Confirmation Notification
    channel.queue_declare(queue='booking_confirmations')
    channel.basic_consume(queue='booking_confirmations', on_message_callback=booking_confirmation_callback, auto_ack=True)

    # Scenario 2: Car Ready for Collection Notification
    channel.queue_declare(queue='car_ready_notifications')
    channel.basic_consume(queue='car_ready_notifications', on_message_callback=car_ready_callback, auto_ack=True)

    # Scenario 3: Car Collected Notification
    channel.queue_declare(queue='car_collected_notifications')
    channel.basic_consume(queue='car_collected_notifications', on_message_callback=car_collected_callback, auto_ack=True)

    # Scenario 4: Booking Cancellation Notification
    channel.queue_declare(queue='booking_cancellation_notifications')
    channel.basic_consume(queue='booking_cancellation_notifications', on_message_callback=booking_cancellation_callback, auto_ack=True)

    print('Waiting for notifications...')
    channel.start_consuming()

if __name__ == "__main__":
    main()
