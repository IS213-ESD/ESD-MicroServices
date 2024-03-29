from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import requests
from invokes import invoke_http
import os, sys

book_charger_bp = Blueprint('book_charger', __name__)

booking_URL = "http://delectric-charging-station:5001/charging-station-booking/create_booking"
station_URL = "http://delectric-charging-station:5001/charging-station/update-charging-status/"
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
            return jsonify(booking_result), 200
            # Check if the booking_result indicates an error

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "book_charger.py internal error: " + ex_str
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
        #return status for error
    else:
        # Invokes payment microservice if booking information is valid and pushed
        print("\nBooking completed.\n")
        print('\n\n-----Invoking payment microservice-----')
        #placeholder for amount
        invoke_http(payment_URL, method="POST", json={'amount':1000})
        print("\nPayment submitted.\n")
        #update charging status to occupied
        print('\n\n-----Invoking update charger microservice-----')
        charger_id = request.json.get('charger_id')
        invoke_http(station_URL + str(charger_id), method="PUT", json={'charging_status': 50})
        print('\n\n-----Invoking update notification microservice-----')
        #to be completed
        return {"message": "Booking completed!"}


    


