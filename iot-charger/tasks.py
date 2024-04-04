from celery_worker import celery, flask_app  # Import the celery instance
from models import db, IotCharger
from invokes import invoke_http
import time
import os

IOT_COMPLEX_BASE = os.getenv('IOT_COMPLEX_BASE')

# celery task to simulate charging
@celery.task
def simulate_charging(charger_id, battery_percentage):
    while battery_percentage < 85:
        battery_percentage += 1
        print(f"Charger {charger_id}: Current charging percentage: {battery_percentage}%")
        query_result = invoke_http(IOT_COMPLEX_BASE + "/iot-complex/update-station", method='POST', json={"charging_station": charger_id, "charging_status": str(battery_percentage)})
        print(query_result)
        if "error" in query_result:
            break # END
        time.sleep(3)  # Simulate charging for 3 second per percentage point
    print(f"Charger {charger_id}: Charging completed")
    # Invoke vacate charger when charging is completed
    result = invoke_http(IOT_COMPLEX_BASE + "/iot-complex/vacate-station", method='POST', json={"charging_station": charger_id})
    print(result)
    

def main():
    simulate_charging(1, 98)
    pass

if __name__ == "__main__":
    main()
