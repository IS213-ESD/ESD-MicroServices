from flask import Flask, request, jsonify, Blueprint, jsonify
from models import ChargingStationBooking, db
import datetime
import requests
import os

handle_booking_bp = Blueprint('booking_complex', __name__, url_prefix='/booking-complex')


@handle_booking_bp.route('/user/<string:user_id>', methods=['GET'])
def get_user_booking_chargers(user_id):
    CHARGING_STATION_URL = os.getenv('CHARGING_STATION_URL')
    BOOKING_USER_URL = os.getenv('BOOKING_USER_URL') + f'{user_id}'
    try:
        chargers_response = requests.get(CHARGING_STATION_URL)
        booking_response = requests.get(BOOKING_USER_URL)
        print(chargers_response, booking_response)
        if chargers_response.status_code != 200 or booking_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data'}), 500

        chargers_data = chargers_response.json().get('chargers')
        booking_data = booking_response.json()

        # Map charger IDs from booking data to charging station data
        user_booked_chargers = []
        for booking in booking_data:
            charger_id = booking.get('charger_id')
            for charger in chargers_data:
                if charger.get('charger_id') == charger_id:
                    booking['charger_info'] = charger
                    user_booked_chargers.append(booking)
                    break
        return jsonify(user_booked_chargers), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@handle_booking_bp.route('/cancelbooking', methods=['POST'])
def post_cancel_booking():
    booking_id = request.json.get('booking_id')
    user_id = request.json.get('user_id')

    BOOKING_BOOKING_URL = os.getenv('BOOKING_BOOKING_URL') + f'{booking_id}'
    CANCEL_BOOKING_URL = os.getenv('CANCEL_BOOKING_URL')
    try:
        booking_response = requests.get(BOOKING_BOOKING_URL)
        if booking_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data'}), 500
        booking_data = booking_response.json()
        if booking_data.get('user_id') != user_id:
            return jsonify({'error': 'Unable to access booking data for the provided user'}), 403

        # If user ID matches, send a POST request to cancel the booking
        cancel_booking_response = requests.post(CANCEL_BOOKING_URL, json={'booking_id': booking_id})
        
        if cancel_booking_response.status_code == 200:
            return jsonify({'message': 'Booking successfully cancelled'}), 200
        else:
            return jsonify({'error': 'Failed to cancel booking'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@handle_booking_bp.route('/endbooking', methods=['POST'])
def post_end_booking():
    booking_id = request.json.get('booking_id')
    user_id = request.json.get('user_id')

    BOOKING_BOOKING_URL = os.getenv('BOOKING_BOOKING_URL')  + f'{booking_id}'
    COMPLETE_BOOKING_URL = os.getenv('COMPLETE_BOOKING_URL')

    try:
        booking_response = requests.get(BOOKING_BOOKING_URL)
        if booking_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data'}), 500
        
        booking_data = booking_response.json()
        print(booking_data)

        if booking_data.get('user_id') != user_id:
            return jsonify({'error': 'Unable to access booking data for the provided user'}), 403

        # If user ID matches, send a POST request to complete the booking
        complete_booking_response = requests.post(COMPLETE_BOOKING_URL, json={'booking_id': booking_id})
        
        if complete_booking_response.status_code == 200:
            return jsonify({'message': 'Booking successfully completed'}), 200
        else:
            return jsonify({'error': 'Failed to complete booking'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
