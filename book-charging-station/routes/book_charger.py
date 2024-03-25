from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import requests
from invokes import invoke_http
import os, sys

book_charger_bp = Blueprint('book_charger', __name__)

booking_URL = "http://delectric-:5001/bookings"
charging_station_URL = "http://delectric-charging-station:5001/"
payment_URL = "http://delectric-payment:5003/create-payment"
# notification_URL = "http://localhost:5003/activity_log"


@book_charger_bp.route("/make-booking", methods=['POST'])
def book_charger():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            info = request.get_json()
            print("\nReceived a payment in JSON:", info)

            # do the actual work
            # 1. Send order info {cart items}
            print('\n-----Invoking payment microservice-----')
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

# @book_charger_bp.route("/book_charger", methods=['POST'])
# def book_charger():
#     # Simple check of input format and data of the request are JSON
#     if request.is_json:
#         try:
#             booking_info = request.get_json()
#             print("\nReceived an order in JSON:", order)

#             # do the actual work
#             # 1. Send order info {cart items}
#             result = processBookCharger(booking_info)
#             return jsonify(result), result["code"]
#             if booking_result.get("code") == 500 and booking_result.get("error") == "Booking overlap detected":
#                 print('Error:', booking_result.get('message'))
#             else:
#             # Handle other cases or success
#                 print('Booking was successful or other error occurred.')

#         except Exception as e:
#             # Unexpected error in code
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
#             print(ex_str)

#             return jsonify({
#                 "code": 500,
#                 "message": "place_order.py internal error: " + ex_str
#             }), 500

#     # if reached here, not a JSON request.
#     return jsonify({
#         "code": 400,
#         "message": "Invalid JSON input: " + str(request.get_data())
#     }), 400


def processBookCharger(info):
    # 2. Send the order info {cart items}
    # Invoke the order microservice
    print('\n-----Invoking booking microservice-----')
    booking_result = invoke_http(booking_URL, method='POST', json=info)
    # Check if the booking_result indicates an error
    if booking_result.get("code") == 500 and booking_result.get("error") == "Booking overlap detected":
        print('Error:', booking_result.get('message'))
    else:
        # Handle other cases or success
        print('\n\n-----Invoking payment microservice-----')
        invoke_http(payment_URL, method="POST", json={'amount':1000})
        print("\nPayment submitted.\n")

    # # Check the order result; if a failure, send it to the error microservice.
    # code = order_result["code"]
    # if code not in range(200, 300):

    # # Inform the error microservice
    #     print('\n\n-----Invoking error microservice as order fails-----')
    #     invoke_http(error_URL, method="POST", json=order_result)
    #     # - reply from the invocation is not used; 
    #     # continue even if this invocation fails
    #     print("Order status ({:d}) sent to the error microservice:".format(
    #         code), order_result)

    
    # # 7. Return error
    #     return {
    #         "code": 500,
    #         "data": {"order_result": order_result},
    #         "message": "Order creation failure sent for error handling."
    #     }

    # # 5. Send new order to shipping
    # # Invoke the shipping record microservice
    # print('\n\n-----Invoking shipping_record microservice-----')
    # shipping_result = invoke_http(
    #     shipping_record_URL, method="POST", json=order_result['data'])
    # print("shipping_result:", shipping_result, '\n')

    # # Check the shipping result;
    # # if a failure, send it to the error microservice.
    # code = shipping_result["code"]
    # if code not in range(200, 300):

    # # Inform the error microservice
    #     print('\n\n-----Invoking error microservice as shipping fails-----')
    #     invoke_http(error_URL, method="POST", json=shipping_result)
    #     print("Shipping status ({:d}) sent to the error microservice:".format(
    #         code), shipping_result)

    # # 7. Return error
    #     return {
    #         "code": 400,
    #         "data": {
    #             "order_result": order_result,
    #             "shipping_result": shipping_result
    #         },
    #         "message": "Simulated shipping record error sent for error handling."
    #     }

    # # 7. Return created order, shipping record
    # return {"code": 201,
    #     "data": {
    #         "order_result": payment_result,
    #         "shipping_result": shipping_result
    #     }
# }

