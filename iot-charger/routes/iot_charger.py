from flask import Flask, request, jsonify, Blueprint, jsonify
from models import IotCharger, db
from invokes import invoke_http
from tasks import simulate_charging
import random

iot_charger_bp = Blueprint('iot_charger', __name__)

# purpose of iot charger is to just trigger completed booking mcsv when 100%

#get all chargers
@iot_charger_bp.route("/iot-chargers")
def get_all_chargers():
    iot_charger_list = IotCharger.query.all()
    return jsonify({"chargers": [iot_charger.json() for iot_charger in iot_charger_list]})

@iot_charger_bp.route("/iot-chargers/<int:charger_id>")
def get_chargers_by_id(charger_id):
    iot_charger_list = IotCharger.query.filter_by(charger_id=charger_id).first()
    if iot_charger_list:
        iot_charger_json = iot_charger_list.json()
        return jsonify(iot_charger_json)
    return jsonify({'error': "No Charger found"}), 500


#start the iot charger
@iot_charger_bp.route("/start-iot-charger/<int:iot_charger_id>")
def start_charger(iot_charger_id):
    iot_charger = IotCharger.query.get(iot_charger_id)     
    if iot_charger:
        if iot_charger.status == 'charging':
            # if the charger is occupied return an error
            return jsonify({"error": "Charger is already charging"}), 400
        # to simulate iot charger, battery percentage is a random int between 70 to 95%
        battery_percentage = random.randint(30, 50)
        #trigger celery task to start charging
        result = simulate_charging.delay(iot_charger_id,battery_percentage)

        #update the status of charging in the iot db
        iot_charger.status = 'charging'
        db.session.commit()
        return jsonify({
            iot_charger_id : 'started'
    }), 202

    return jsonify({"error": "Charger not found"}), 404


# manual trigger to end the charging
# @iot_charger_bp.route("/iot-charger-trigger")
# def manual_set_charger_complete():
#     results = invoke_http("http://delectric-payment:5003/payments", method='GET')
#     # Add additional logic here if needed
#     return jsonify(results)

#fucntion that will be called by the celery task to update the status in iot db to indicate charging has been completed
@iot_charger_bp.route("/vacate-charger", methods=['POST'])
def vacate_charger():
    data = request.get_json()
    iot_charger = IotCharger.query.get(data['charger_id'])
    if iot_charger:
        iot_charger.status = 'vacant'
        db.session.commit()
        return jsonify({"message": f"Charger {data['charger_id']} status updated to vacant"}), 200
    else:
        return jsonify({"error": "Charger not found"}), 404

