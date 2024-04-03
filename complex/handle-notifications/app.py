import os
from os import environ
import pika
import requests
import json
import time  # Import the time module for sleep

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
GET_USER_DETAILS_URL = USER_BASE + "/getuserdetails/"

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
    

def get_userdetails(user_id):
    try:
        GET_USER_DETAILS_BY_ID = GET_USER_DETAILS_URL + f'{user_id}'
        user_response = requests.get(GET_USER_DETAILS_BY_ID)
        if user_response.status_code != 200:
            return {'error': 'Failed to fetch data', 'code': 500}
        user_data = user_response.json()
        phone = user_data['phone']
        return phone
    except Exception as e:
        return None
    

def booking_confirmation_callback(ch, method, properties, body):
    try:
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
            message_str = 'Booking Confirmation\n' + booking_details
            userdetails = get_userdetails(user_id)
            if userdetails:
                phone = userdetails
                send_user_notification(message_str, phone)
                print("Cancellation notification sent successfully.")
            else:
                print('Failed to retrieve user details')
        else:
            print("Failed to retrieve booking details")
    except requests.exceptions.RequestException as e:
        print("Failed to send notification:", e)

def user_sms_notifications(ch, method, properties, body):
    body_str = body.decode('utf-8')  # Decode byte string to string
    body_dict = json.loads(body_str)  # Convert string to dictionary
    send_user_notification(body_dict.get('msg'), "83217652")

def user_sms_notifications(ch, method, properties, body):
    body_str = body.decode('utf-8')  # Decode byte string to string
    body_dict = json.loads(body_str)  # Convert string to dictionary
    send_user_notification(body_dict.get('msg'), "83217652")

def car_ready_callback(ch, method, properties, body):
    print("Received car ready notification:", body)

def car_collected_callback(ch, method, properties, body):
    print("Received car collected notification:", body)

def booking_cancellation_callback(ch, method, properties, body):
    try:
        print("Received booking cancellation notification:", body)
        # Decode the body from bytes to string
        body_str = body.decode('utf-8')
        
        # Parse the JSON string into a Python dictionary
        request_data = json.loads(body_str)
        booking_id = request_data.get('booking_id')
        user_id = request_data.get("user_id")
        crafted_msg = request_data.get("msg", False)
        if crafted_msg is False:
            # Retrieve booking details
            booking_details = get_booking_details(booking_id)
            message_str = 'Booking Cancellation\n' + booking_details
        userdetails = get_userdetails(user_id)
        if userdetails:
            phone = userdetails
            send_user_notification(crafted_msg, phone)
            print("Cancellation notification sent successfully.")
        else:
            print('Failed to retrieve user details')
    except requests.exceptions.RequestException as e:
        print("Failed to send notification:", e)

def late_collection_callback(ch, method, properties, body):
    try:
        print("Received late collection message:", body)
        body_str = body.decode('utf-8')
        request_data = json.loads(body_str)
        user_id = request_data['user_id']
        msg = request_data['msg']
        userdetails = get_userdetails(user_id)
        if userdetails:
            phone = userdetails
            send_user_notification(msg, phone)
            print("Late notification sent successfully.")
        else:
            print('Failed to retrieve user details')
    except requests.exceptions.RequestException as e:
        print("Failed to send notification:", e)

def refund_callback(ch, method, properties, body):
    try:
        print("Received refund message:", body)
        body_str = body.decode('utf-8')
        request_data = json.loads(body_str)
        user_id = request_data['user_id']
        msg = request_data['msg']
        userdetails = get_userdetails(user_id)
        if userdetails:
            phone = userdetails
            send_user_notification(msg, phone)
            print("Refund notification sent successfully.")
        else:
            print('Failed to retrieve user details')
    except requests.exceptions.RequestException as e:
        print("Failed to send notification:", e)

def booking_complete_callback(ch, method, properties, body):
    print("Booking complete message:", body)
    try:
        body_str = body.decode('utf-8')
        request_data = json.loads(body_str)
        user_id = request_data['user_id']
        charging_fee = request_data['charging_fee']
        msg = f"Booking Completed!\n\nA usage fee of ${charging_fee} have been charged to your card. Thanks for using Deletric."
        userdetails = get_userdetails(user_id)
        if userdetails:
            phone = userdetails
            send_user_notification(msg, phone)
            print("Complete notification sent successfully.")
        else:
            print('Failed to retrieve user details')
        pass
    except requests.exceptions.RequestException as e:
        print("Failed to send notification:", e)

def connect_to_rabbitmq():
    attempts = 0
    while True:
        try:
            print(f"Trying to connect to RabbitMQ (attempt {attempts + 1})")
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(RABBITMQHOST)
            connection = pika.BlockingConnection(parameters)
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            attempts += 1
            print(f"Failed to connect to RabbitMQ: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

def main():
    print("Running Handle Notifications")
    connection = connect_to_rabbitmq()
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

    # Scenario 5: Send SMS Notification for upcoming 
    channel.queue_declare(queue='user_sms_notifications')
    channel.basic_consume(queue='user_sms_notifications', on_message_callback=user_sms_notifications, auto_ack=True)

    # Scenario 5: Late Collection Notification
    channel.queue_declare(queue='late_collection_notifications')
    channel.basic_consume(queue='late_collection_notifications', on_message_callback=late_collection_callback, auto_ack=True)

    # Scenario 6: Refund Notification
    channel.queue_declare(queue='refund_notifications')
    channel.basic_consume(queue='refund_notifications', on_message_callback=refund_callback, auto_ack=True)

    # Booking Ends
    channel.queue_declare(queue='booking_complete_notifications')
    channel.basic_consume(queue='booking_complete_notifications', on_message_callback=booking_complete_callback, auto_ack=True)

    print('Waiting for notifications...')
    channel.start_consuming()

if __name__ == "__main__":
    main()
