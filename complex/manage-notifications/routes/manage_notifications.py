from flask import Flask, request, jsonify, Blueprint
from invokes import invoke_http
import os, sys

manage_notifications_bp = Blueprint('manage_notifications', __name__)

notification_URL = "http://delectric-payment:5003/send-notification"
user_URL = "http://user:5002/getuserdetails/"

# send notification to inform that booking is ending
@manage_notifications_bp.route("/send-notification", methods=['POST'])
def send_notification():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            info = request.get_json()
            # 1. Send booking info
            print('\n-----Invoking complex notification microservice-----')
            notification_result = processNotification(info)
            print('\n------------------------')
            print('\nresult: ', notification_result)
            return jsonify(notification_result), 200
            # Check if the booking_result indicates an error

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "manage_notification.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processNotification(info):
    # Get user number
    user_info = invoke_http(user_URL+str(info.get('user_id')), method="GET")
    phone = user_info.get('phone')

    print('\n-----Invoking notification microservice-----')
    notification_result = invoke_http(notification_URL, method='POST', json={info.get('msg'), phone})
    if notification_result.get("code") == 400:
        print('Error:', notification_result.get('message'))
        #return status for error
    else:
        # Invokes payment microservice if booking information is valid and pushed
        print("\nSend-Notification completed.\n")
        #to be completed
        return {"message": "Notification sent!"}


    


