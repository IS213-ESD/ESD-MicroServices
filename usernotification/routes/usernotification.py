from twilio.rest import Client
import os 
from dotenv import load_dotenv
from flask import request, jsonify, Blueprint, jsonify
import json


# Load environment variables from .env file
load_dotenv()


account_sid = os.getenv('ACCOUNT_SID')
twilio_num = os.getenv('TWILIO_NUM')
auth_token = os.getenv('AUTH_TOKEN')
client = Client(account_sid, auth_token)


notif_bp = Blueprint('usernotification', __name__)


# Send notification endpoint
@notif_bp.route("/sendnotification", methods=["POST"])
def sendnotification():
  try:
    data = request.json
    # get user's phone number and message to be sent
    msg = data["msg"]
    phone = data["phone"]
    if '+65' not in phone:
      phone = '+65' + phone
    # send message to user using Twilio virtual number
    # message = client.messages.create(
    #   body=msg,
    #   from_=twilio_num,
    #   to=phone
    # )
    # print(message.json())
    print(f"[Simulate message send] {phone}: {msg}")
    return jsonify({
      "code": 200,
      "message": "Message sent successfully."
    })
  except Exception as e:
    # Return error response
    return jsonify({
        "code": 400,
        "message": f"Send Notification failed. {e}"
        
    }), 400

