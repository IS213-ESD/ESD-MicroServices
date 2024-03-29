from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import requests
from invokes import invoke_http
import os, sys

book_charger_bp = Blueprint('book_charger', __name__)

booking_URL = "http://delectric-charging-station:5001/create_booking"
station_URL = "http://delectric-charging-station:5001/update-charging-status/"
payment_URL = "http://delectric-payment:5004/create-payment"

# to invoke "Make booking" process
@book_charger_bp.route("/make-booking", methods=['POST'])
def book_charger():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            info = request.get_json()
            print("\nReceived a booking in JSON:", info)

            # 1. Send booking info
            print('\n-----Invoking complex booking microservice-----')
            booking_result = processBookCharger(info)
            print('\n------------------------')
            print('\nresult: ', booking_result)
            return jsonify(booking_result), booking_result["code"]
            # Check if the booking_result indicates an error

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processBookCharger(info):
    # Invoke the booking microservice
    print('\n-----Invoking booking microservice-----')
    booking_result = invoke_http(booking_URL, method='POST', json=info)
    # Check if the booking_result indicates an error (overlap or no existing charger)
    if booking_result.get("code") == 500:
        print('Booking failed.', booking_result.get('error'))
        print('Error:', booking_result.get('message'))
    else:
        # Invokes payment microservice if booking information is valid and pushed
        print("\nBooking completed.\n")
        print('\n\n-----Invoking payment microservice-----')
        invoke_http(payment_URL, method="POST", json={'amount':1000})
        print("\nPayment submitted.\n")