from flask import Flask, request, jsonify, Blueprint, jsonify
from models import IotCharger, db
from invokes import invoke_http
from tasks import simulate_charging
import random

iot_charger_bp = Blueprint('iot_charger', __name__)

# purpose of iot charger is to just trigger completed booking mcsv when 100%
@iot_charger_bp.route("/iot-chargers")
def get_all_chargers():
    iot_charger_list = IotCharger.query.all()
    return jsonify({"chargers": [iot_charger.json() for iot_charger in iot_charger_list]})

@iot_charger_bp.route("/start-iot-charger/<int:iot_charger_id>")
def start_charger(iot_charger_id):
    iot_charger = IotCharger.query.get(iot_charger_id)     
    if iot_charger:
        if iot_charger.status == 'charging':
            return jsonify({"error": "Charger is already charging"}), 400
        battery_percentage = random.randint(70, 95)
        result = simulate_charging.delay(iot_charger_id,battery_percentage)
        iot_charger.status = 'charging'
        db.session.commit()
        return jsonify({
            iot_charger_id : 'started'
    }), 202

    return jsonify({"error": "Charger not found"}), 404


# function tbc // waiting for complete booking microservice // manual trigger // will remap to complete booking
@iot_charger_bp.route("/iot-charger-trigger")
def manual_set_charger_complete():
    results = invoke_http("http://delectric-payment:5003/payments", method='GET')
    # Add additional logic here if needed
    return jsonify(results)

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

