from flask import Flask, request, jsonify, Blueprint, jsonify
from models import IotCharger, db
from invokes import invoke_http
from flask_executor import Executor
import time
import random

iot_charger_bp = Blueprint('iot_charger', __name__)
executor = Executor()

def create_app():
    app = Flask(__name__)
    app.config['EXECUTOR_TYPE'] = 'thread'
    app.config['EXECUTOR_MAX_WORKERS'] = 2
    app.config['EXECUTOR_PUSH_APP_CONTEXT'] = True
    executor.init_app(app)
    return app

app = create_app()

# purpose of iot charger is to just trigger completed booking mcsv when 100%
@iot_charger_bp.route("/iot-chargers")
def get_all_chargers():
    iot_charger_list = IotCharger.query.all()
    return jsonify({"chargers": [iot_charger.json() for iot_charger in iot_charger_list]})

def simulate_charging(charger_id, battery_percentage):
    while battery_percentage < 100:
        battery_percentage += 1
        print(f"Charger {charger_id}: Current charging percentage: {battery_percentage}%")
        time.sleep(1)  # Simulate charging for 1 second per percentage point
    print(f"Charger {charger_id}: Charging completed")
    # Invoke another function when charging is completed
    # For example: invoke_http("http://your-service/complete", method='POST', json={"charger_id": charger_id})

@iot_charger_bp.route("/start-iot-charger/<int:iot_charger_id>")
def start_charger(iot_charger_id):
    iot_charger = IotCharger.query.get(iot_charger_id)     
    if iot_charger:
        battery_percentage = random.randint(15, 95)
        executor.submit(simulate_charging, iot_charger_id, battery_percentage)
        return jsonify({"charger": iot_charger.json(), "status": "Charging started"})

    return jsonify({"error": "Charger not found"}), 404

# function tbc // waiting for complete booking microservice // manual trigger // will remap to complete booking
@iot_charger_bp.route("/iot-charger-trigger")
def manual_set_charger_complete():
    results = invoke_http("http://delectric-payment:5003/payments", method='GET')
    # Add additional logic here if needed
    return jsonify(results)
