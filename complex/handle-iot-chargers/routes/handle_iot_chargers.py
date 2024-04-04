from flask import Flask, request, jsonify, Blueprint, jsonify
import datetime
import requests
import os
import json

handle_iot_chargers_bp = Blueprint('iot_complex', __name__, url_prefix='/iot-complex')

BASE_IOT_GET_CHARGERS_BY_ID_URL = os.getenv('IOT_GET_CHARGERS_BY_ID_URL')
BASE_UPDATE_CHARGING_STATUS_URL = os.getenv('UPDATE_CHARGING_STATUS_URL')
BASE_REMOVE_CHARGING_STATUS_URL = os.getenv('REMOVE_CHARGING_STATUS_URL')
IOT_SIMPLE_BASE = os.getenv('IOT_SIMPLE_BASE')
CHARGING_STATION_BOOKING_BASE = os.getenv('CHARGING_STATION_BOOKING_BASE')
CHARGING_FEE_PER_USE = 1 # Set charging fee per sec
headers = {'Content-Type': 'application/json'}   

@handle_iot_chargers_bp.route('/update-station', methods=['POST'])
def iot_update_charging_status():
    try:
        data = request.get_json()
        charging_station = data.get('charging_station')  # Find charger ID
        charging_status = data.get('charging_status')  # Percentage

        if charging_station is None:
            return jsonify({'error': 'Charging station ID is missing'}), 400
        if charging_status is None:
            return jsonify({'error': 'Charging status is missing'}), 400
        
        IOT_GET_CHARGERS_BY_ID_URL = BASE_IOT_GET_CHARGERS_BY_ID_URL + str(charging_station)
        UPDATE_CHARGING_STATUS_URL = BASE_UPDATE_CHARGING_STATUS_URL + str(charging_station)
        iot_chargers_response = requests.get(IOT_GET_CHARGERS_BY_ID_URL)
        if iot_chargers_response.status_code != 200:
            return jsonify({'error': 'Failed to fetch data'}), 500

        iot_charger_data = iot_chargers_response.json()
        if iot_charger_data.get('status') != 'charging':
            # UPDATE to charger station to reflect not charging
            # requests.put(REMOVE_CHARGING_STATUS_URL, headers=headers)
            return jsonify({'error': 'Terminate IOT Worker'}), 403
        
        update_charging_status_response = requests.put(UPDATE_CHARGING_STATUS_URL, 
                                                       data=json.dumps({"charging_status": charging_status}), 
                                                       headers=headers)
        if update_charging_status_response.status_code != 200:
            return jsonify({'error': 'Failed to update data'}), 500
        make_charing_fee = iot_find_current_booking(charging_station)
        if make_charing_fee is None:
            return jsonify({'error': 'Failed to update booking'}), 500
        return jsonify(update_charging_status_response.json()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@handle_iot_chargers_bp.route('/vacate-station', methods=['POST'])
def iot_remove_charging_status():
    try:
        data = request.get_json()
        charging_station = data.get('charging_station')  # Find charger ID
        REMOVE_CHARGING_STATUS_URL = BASE_REMOVE_CHARGING_STATUS_URL + str(charging_station)
        remove_charging_status_response = requests.put(REMOVE_CHARGING_STATUS_URL, headers=headers)
        remove_iot_charging_status_response = requests.post(IOT_SIMPLE_BASE + "/vacate-charger", json={"charger_id": charging_station}, headers=headers)
        if remove_charging_status_response.status_code != 200 or remove_iot_charging_status_response.status_code != 200:
            return jsonify({'error': 'Failed to update data'}), 500
        response_data = {
            **remove_charging_status_response.json(),
            **remove_iot_charging_status_response.json()
        }
        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def iot_find_current_booking(charging_station):
    try:
        GET_BOOKINGS_BY_CHARGER_ID =  CHARGING_STATION_BOOKING_BASE + f"/charger/{charging_station}"
        get_booking_by_charger_id_response = requests.get(GET_BOOKINGS_BY_CHARGER_ID)
        if get_booking_by_charger_id_response.status_code != 200:
            return None
        get_booking_by_charger_id_data = get_booking_by_charger_id_response.json()
        current_time = datetime.datetime.now()
        for booking in get_booking_by_charger_id_data:
            booking_id = booking.get("booking_id")
            booking_datetime = datetime.datetime.strptime(booking["booking_datetime"].strip(), '%Y-%m-%d %H:%M:%S')
            booking_duration_hours = booking.get("booking_duration_hours")
            booking_end_time = booking_datetime + datetime.timedelta(hours=booking_duration_hours)
            if booking_datetime < current_time < booking_end_time:
                print("[Within slot]", booking_id, booking_end_time)
                update_booking_charging_fee_url = CHARGING_STATION_BOOKING_BASE + f"/update_charging_fee/{booking_id}"
                update_booking_charging_fee_response = requests.post(update_booking_charging_fee_url, json={"charging_fee": CHARGING_FEE_PER_USE})
                if update_booking_charging_fee_response.status_code != 200:
                    return None
                break
        return True
    except Exception as e:
        return None
    

