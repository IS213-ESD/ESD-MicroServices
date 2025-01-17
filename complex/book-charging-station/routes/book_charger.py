from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import requests
from invokes import invoke_http
import os
import datetime
import pika
import json

book_charger_bp = Blueprint('book_charger', __name__, url_prefix='/book-charger-complex')

# booking_URL = os.getenv('CHARGING_STATION_BOOKING_BASE') + "/create_booking"
# station_URL = os.getenv('CHARGING_STATION_BASE') + "/update-charging-status/"
# payment_URL = os.getenv('PAYMENT_BASE') + "/create-payment"

CHARGING_STATION_BOOKING_BASE = os.getenv('CHARGING_STATION_BOOKING_BASE')
CHARGING_STATION_BASE = os.getenv('CHARGING_STATION_BASE')
PAYMENT_BASE = os.getenv('PAYMENT_BASE')
USER_BASE_URL = os.getenv('USER_BASE')
RABBITMQHOST = os.getenv('RABBITMQHOST')

@book_charger_bp.route("/book-charger", methods=['POST'])
def book_charger():
    try:
        print(request.json)
        user_id = request.json.get('user_id')
        user_payment_details_url = f"{USER_BASE_URL}/getpaymentdetails/{user_id}"
        payment_details_response = requests.get(user_payment_details_url)
        if payment_details_response.status_code != 200:
            return jsonify({'error': 'Failed to retrieve payment details'}), 500
        
        # Extract the payment token from the response
        payment_token = payment_details_response.json().get('payment_token')
        if not payment_token:
            return jsonify({'error': 'Payment token not found in response'}), 500
        
        # Check Booking Overlap 
        # Make a booking to the charging station booking service
        booking_url = f"{CHARGING_STATION_BOOKING_BASE}/create_booking"
        booking_data = {
            "charger_id": request.json.get('charger_id'),
            "user_id": request.json.get('user_id'),
            "booking_datetime": request.json.get('booking_datetime'),
            "booking_duration_hours": request.json.get('booking_duration_hours'),
            "booking_status": "PENDING"
        }
        booking_response = requests.post(booking_url, json=booking_data)
        booking_id = booking_response.json().get("booking_id")
        print("[BOOKING RESPONSE]", booking_response.json())
        # Check if the booking was successful
        if booking_response.status_code != 201:
            return jsonify({'error': 'Failed to make booking, Booking overlap Detected'}), 500

        # Make payment
        create_payment_url = f"{PAYMENT_BASE}/create-payment"
        payment_data = {
            "amount": request.json.get('booking_duration_hours') * 10,
            "payment_method_id": payment_token
        }
        payment_response = requests.post(create_payment_url, json=payment_data)
        print("[PAYMENT RESPONSE]", payment_response.json())
        if payment_response.status_code != 200:
            return jsonify({'error': 'Error Making Payment'}), 500
        payment_id = payment_response.json().get('status') # Points to payment ID
        print("[PAYMENT_ID]", payment_id)
        # Update Booking with Payment TOKEN and Update Status to 'IN_PROGRESS'
        update_booking_url = f"{CHARGING_STATION_BOOKING_BASE}/update_booking/{booking_id}"
        update_booking_data = {
            "payment_id": payment_id
        }
        payment_response = requests.post(update_booking_url, json=update_booking_data)
        message = {'booking_id': booking_id, 'user_id': user_id}
        json_message = json.dumps(message)
        print("[Create Booking] Sending out notification (booking_confirmation_callback)", json_message)
        send_notification('booking_confirmations', json_message)
        return jsonify(booking_response.json()), 200
    except Exception as e:
        return jsonify({
                "code": 500,
                "message": "book_charger.py internal error"
            }), 500

@book_charger_bp.route("/cancel-booking", methods=['POST'])
def cancel_booking():
    try:
        # user_id = request.json.get('user_id')
        booking_id = request.json.get('booking_id')
        # GET PAYMENT ID From booking
        get_booking_by_id_url = f"{CHARGING_STATION_BOOKING_BASE}/booking/{booking_id}"
        get_booking_response = requests.get(get_booking_by_id_url)
        if get_booking_response.status_code != 200:
            return jsonify({'error': 'Error with Retrieving Booking Information'}), 500
        payment_id = get_booking_response.json().get('payment_id') 
        user_id = get_booking_response.json().get('user_id') 

        # Cancel Booking on - charging-station-booking
        cancel_booking_url = f"{CHARGING_STATION_BOOKING_BASE}/cancel_booking"
        cancel_booking_data = {
            "booking_id": booking_id
        }
        cancel_booking_response = requests.post(cancel_booking_url, json=cancel_booking_data)
        if cancel_booking_response.status_code != 200:
            return jsonify({'error': 'Error with Booking Cancellation'}), 500
        
        # Trigger Refund
        refund_payment_url = f"{PAYMENT_BASE}/create-refund"
        refund_payment_data = {
            "payment_id": payment_id
        }
        print("REFUND amt", refund_payment_data)
        refund_payment_response = requests.post(refund_payment_url, json=refund_payment_data)
        if refund_payment_response.status_code != 200:
            return jsonify({'error': 'Error with Payment Refund'}), 500
        
        message = {'booking_id': booking_id, 'user_id': user_id}
        json_message = json.dumps(message)
        print("[Cancel Booking] Sending out notification (booking_cancellation_callback)", json_message)
        send_notification('booking_cancellation_notifications', json_message)
        return jsonify({'message': "Booking Cancelled"}), 200
    except Exception as e:
        return jsonify({
                "code": 500,
                "message": "book_charger.py internal error"
            }), 500


@book_charger_bp.route("/complete-booking", methods=['POST'])
def complete_booking():
    try:
        # user_id = request.json.get('user_id')
        booking_id = request.json.get('booking_id')
        # GET PAYMENT ID From booking
        get_booking_by_id_url = f"{CHARGING_STATION_BOOKING_BASE}/booking/{booking_id}"
        get_booking_response = requests.get(get_booking_by_id_url)
        if get_booking_response.status_code != 200:
            return jsonify({'error': 'Error with Retrieving Booking Information'}), 500
        payment_id = get_booking_response.json().get('payment_id') 
        booking_datetime_str = get_booking_response.json().get('booking_datetime')
        booking_status = get_booking_response.json().get('booking_status') 
        booking_duration_hours = get_booking_response.json().get('booking_duration_hours') 
        booking_charging_fee = get_booking_response.json().get('charging_fee') 
        user_id = get_booking_response.json().get('user_id') 
        if booking_status != "IN_PROGRESS":
            return jsonify({'error': 'No Active Booking'}), 500

        # Cancel Booking on - charging-station-booking
        complete_booking_url = f"{CHARGING_STATION_BOOKING_BASE}/complete_booking"
        complete_booking_data = {
            "booking_id": booking_id
        }
        complete_booking_response = requests.post(complete_booking_url, json=complete_booking_data)
        if complete_booking_response.status_code != 200:
            return jsonify({'error': 'Error with Booking Cancellation'}), 500
        
        # GET USER PAYMENT TOKEN
        user_payment_details_url = f"{USER_BASE_URL}/getpaymentdetails/{user_id}"
        payment_details_response = requests.get(user_payment_details_url)
        if payment_details_response.status_code != 200:
            return jsonify({'error': 'Failed to retrieve payment details'}), 500
        payment_token = payment_details_response.json().get('payment_token')
        if not payment_token:
            return jsonify({'error': 'Payment token not found in response'}), 500
        # Trigger Charge for Charging fee
        create_payment_url = f"{PAYMENT_BASE}/create-payment"
        payment_data = {
            "amount": booking_charging_fee,
            "payment_method_id": payment_token
        }
        payment_response = requests.post(create_payment_url, json=payment_data)
        print("[PAYMENT RESPONSE]", payment_response.json())
        if payment_response.status_code != 200:
            return jsonify({'error': 'Error Making Payment'}), 500
        payment_id = payment_response.json().get('status') # Points to payment ID

        
        message = {'booking_id': booking_id, 'user_id': user_id, 'charging_fee': booking_charging_fee}
        json_message = json.dumps(message)
        print("[Booking Complete] Sending out notification (booking_complete_notifications)", json_message)
        send_notification('booking_complete_notifications', json_message)
        return jsonify({'message': "Booking Complete"}), 200
    except Exception as e:
        return jsonify({
                "code": 500,
                "message": "book_charger.py internal error"
            }), 500


# # to invoke "Make booking" process
# @book_charger_bp.route("/make-booking", methods=['POST'])
# def book_charger():
#     # Simple check of input format and data of the request are JSON
#     if request.is_json:
#         try:
#             info = request.get_json()
#             print("\nReceived a booking in JSON:", info)

#             # 1. Send booking info
#             print('\n-----Invoking complex booking microservice-----')
#             booking_result = processBookCharger(info)
#             print('\n------------------------')
#             print('\nresult: ', booking_result)
#             return jsonify(booking_result), 200
#             # Check if the booking_result indicates an error

#         except Exception as e:
#             # Unexpected error in code
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
#             print(ex_str)

#             return jsonify({
#                 "code": 500,
#                 "message": "book_charger.py internal error: " + ex_str
#             }), 500

#     # if reached here, not a JSON request.
#     return jsonify({
#         "code": 400,
#         "message": "Invalid JSON input: " + str(request.get_data())
#     }), 400

# def processBookCharger(info):
#     # Invoke the booking microservice
#     print('\n-----Invoking booking microservice-----')
#     booking_result = invoke_http(booking_URL, method='POST', json=info)
#     # Check if the booking_result indicates an error (overlap or no existing charger)
#     if booking_result.get("code") == 500:
#         print('Booking failed.', booking_result.get('error'))
#         print('Error:', booking_result.get('message'))
#         #return status for error
#     else:
#         # Invokes payment microservice if booking information is valid and pushed
#         print("\nBooking completed.\n")
#         print('\n\n-----Invoking payment microservice-----')
#         #placeholder for amount
#         invoke_http(payment_URL, method="POST", json={'amount':1000})
#         print("\nPayment submitted.\n")
#         #update charging status to occupied
#         print('\n\n-----Invoking update charger microservice-----')
#         charger_id = request.json.get('charger_id')
#         invoke_http(station_URL + str(charger_id), method="PUT", json={'charging_status': 50})
#         print('\n\n-----Invoking update notification microservice-----')
#         #to be completed
#         return {"message": "Booking completed!"}


    
# SEND NOTIFICATION via AMQP
def send_notification(queue_name, message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQHOST))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(exchange='', routing_key=queue_name, body=message)
        print(f"Sent notification to {queue_name}: {message}")
        connection.close()
    except Exception as e:
        print("ERROR CONNECTING TO AMQP")
        return {}

