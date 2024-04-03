from flask import Flask, request, jsonify, Blueprint, jsonify
import datetime
import requests
import os
import pika
import json


handle_late_collection_bp = Blueprint('late_complex', __name__, url_prefix='/late_complex')


@handle_late_collection_bp.route('/handle_late_collection', methods=['PUT'])
def handle_late():
    try:
        data = request.get_json()
        booking_id = data['booking_id']
        # Begin handling late collection process
        BOOKING_BOOKING_URL = os.getenv('BOOKING_BOOKING_URL') + f'{booking_id}'
        # invoke charging station booking microservice
        booking_response = requests.get(BOOKING_BOOKING_URL)
        if booking_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data'}), 500

        # get booking information
        booking_data = booking_response.json()
        user_id = booking_data['user_id']
        charger_id = booking_data['charger_id']

        # create message to be sent to late customer

        late_message = "Dear Customer, \n\nWe regret to inform you that your scheduled car collection time was missed, and your vehicle remains uncollected past the agreed-upon time. As a result, we must emphasize the importance of collecting your car as soon as possible to avoid further inconvenience. We would like to kindly remind you that late collection will result in additional charges as outlined in our terms and conditions. \n\nWe appreciate your prompt attention to this matter and your cooperation in resolving the situation swiftly."
        message = {'user_id': user_id, 'msg': late_message}
        json_message = json.dumps(message)

        # AMQP - send message to late_collection_notifications queue
        send_notification('late_collection_notifications', json_message)
        booking_datetime_str = booking_data['booking_datetime']
        booking_duration_hours = booking_data['booking_duration_hours']
        booking_datetime = datetime.datetime.strptime(booking_datetime_str, "%a, %d %b %Y %H:%M:%S %Z")
        booking_end_time = booking_datetime + datetime.timedelta(hours=booking_duration_hours)

        # check if theres any upcoming booking that will be affected
        check_response = checknextbooking(charger_id, booking_end_time)
        if check_response['code'] != 200:
            return jsonify({'error': 'Failed to send message'}), 500

        # flag == 1: yes, theres upcoming booking affected --> handle next booking
        if check_response['flag'] == 1:
            next_booking_id = check_response['booking_id']
            next_user_id = check_response['user_id']
            next_payment_id = check_response['payment_id']
            next_booking_response = handlenextbooking(next_booking_id, next_user_id, next_payment_id)

            if next_booking_response['code'] != 200:
                return jsonify({'error': 'Failed to handle next booking'}), 500

        # no next booking / after next booking handled --> charge late customer
        late_response = latecharge(user_id)
        if late_response['code'] != 200:
            return jsonify({'error': 'Failed to charge late fees'}), 500
        return jsonify({'message': 'Late Collection handled successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def checknextbooking(charger_id, booking_end_time):
    # invoke booking charger microservice to check if theres any upcoming bookings affected
    try:
        BOOKING_CHARGER_URL = os.getenv('BOOKING_CHARGER_URL') + f'{charger_id}'
        charger_response = requests.get(BOOKING_CHARGER_URL)
        if charger_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data'}), 500
        charger_data = charger_response.json()
        for charger in charger_data:
            bookingtime_str = charger['booking_datetime']
            bookingtime = datetime.datetime.strptime(bookingtime_str, "%a, %d %b %Y %H:%M:%S %Z")

            # if theres a booking time that coincides with the late booking, return flag = 0
            if bookingtime == booking_end_time:
                return {
                    'flag': 1,
                    'user_id': charger['user_id'],
                    'booking_id': charger['booking_id'],
                    'payment_id': charger['payment_id'],
                    'code': 200
                }

        # else if no affected bookings, return flag = 0
        return {
            'flag': 0,
            'code': 200
        }
    except Exception as e:
        return {'error': str(e), 'code': 500}

def handlenextbooking(booking_id, user_id, payment_id):
    try:
        # create message to be sent to affected customer about cancelling booking
        cancellation_msg = "Dear customer, \n\nWe regret to inform you that your scheduled car collection appointment has been canceled due to unforeseen circumstances. Despite our best efforts to accommodate your appointment, the previous customer's delay in collecting their vehicle has disrupted our schedule. \n\nAs a gesture of goodwill, we would like to offer you a full refund for any inconvenience caused by the cancellation of your appointment."
        message = {'user_id': user_id, 'msg': cancellation_msg}
        json_message = json.dumps(message)
        
        # AMQP - send message to booking_cancellation_notifications queue
        send_notification('booking_cancellation_notifications', json_message)

        # call booking microservice to cancel booking
        BOOKING_CANCEL = os.getenv('BOOKING_CANCEL')
        cancellation_response = requests.post(BOOKING_CANCEL, json=
        {
            'booking_id': booking_id
        })
        if cancellation_response.status_code != 200:
            return {'error': 'Failed to cancel booking', 'code':500}
        
        # after booking cancelled, proceed with refund - call payments microservice and proceed with creating full refund
        REFUND = os.getenv('REFUND')
        refund_response = requests.post(REFUND, json=
        {
            'payment_id': payment_id
        })
        if refund_response.status_code != 200:
            return {'error': 'Failed to refund', 'code':500}
        
        # create refund message to be sent to affected customer 
        refund_msg = "Dear customer, \n\n the full amount has been refunded to your account. \n\nWe apologise for the inconvenience caused, and we hope to see you again!"
        message = {'user_id': user_id, 'msg': refund_msg}
        json_message = json.dumps(message)

        # AMQP - send message to refund_notifications queue
        send_notification('refund_notifications', json_message)
        return {'message': 'Refund successful', 'code':200}

    except Exception as e:
        return {'error': str(e), 'code':500}

def latecharge(user_id):
    # invoke user microservice to get user payment token
    try:
        GET_USER_PAYMENT_URL = os.getenv('GET_USER_PAYMENT_URL') + f'{user_id}'
        user_response = requests.get(GET_USER_PAYMENT_URL)
        if user_response.status_code != 200:
            return {'error': 'Failed to fetch data', 'code': 500}
        user_data = user_response.json()
        payment_id = user_data['payment_token']
        # invoke payment microservice to create charge
        PAYMENT = os.getenv('PAYMENT')
        payment_response = requests.post(PAYMENT, json=
        {
            'amount': 50,
            'payment_method_id': payment_id # change to get from userdb
        })
        if payment_response.status_code != 200:
            return {'error': 'Failed to charge late customer', 'code':500}

        # create message to be sent to late customer about late charge
        late_charge_msg = "Dear customer, \n\nwe regret to inform you that a late charge fee of $50 has been deducted from your bank account."
        message = {'user_id': user_id, 'msg': late_charge_msg}
        json_message = json.dumps(message)

        # AMQP - send message to late_collection_notifications queue
        send_notification('late_collection_notifications', json_message)
        return {'message': 'Late Charge successful', 'code':200}

    except Exception as e:
        return {'error': str(e), 'code':500}


def send_notification(queue_name, message):
    RABBITMQHOST = os.getenv('RABBITMQHOST')
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQHOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)    
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(f"Sent notification to {queue_name}: {message}")
    connection.close()
