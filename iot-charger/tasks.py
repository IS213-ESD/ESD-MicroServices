from celery_worker import celery, flask_app  # Import the celery instance
from models import db, IotCharger
from invokes import invoke_http
import time

@celery.task
def simulate_charging(charger_id, battery_percentage):
    while battery_percentage < 100:
        battery_percentage += 1
        print(f"Charger {charger_id}: Current charging percentage: {battery_percentage}%")
        time.sleep(1)  # Simulate charging for 1 second per percentage point
    print(f"Charger {charger_id}: Charging completed")
    invoke_http("http://delectric-iot-charger:5002/vacate-charger", method='POST', json={"charger_id": charger_id})
    # Invoke another function when charging is completed
    
