from flask import Flask, request, jsonify, Blueprint, jsonify
from models import IotCharger, db
from invokes import invoke_http

iot_charger_bp = Blueprint('iot_charger', __name__)

# purpose of iot charger is to just trigger completed booking mcsv when 100%

@iot_charger_bp.route("/iot-chargers")
def get_all_chargers():
    iot_charger_list = IotCharger.query.all()
    return jsonify({"chargers": [iot_charger.json() for iot_charger in iot_charger_list]})

# function tbc // waiting for complete booking microservice
@iot_charger_bp.route("/iot-charger-complete")
def set_charger_complete():
    iot_charger_list = IotCharger.query.all()
    # to send notification that charging is complete
    # invoke_http(shipping_record_URL, method="POST", json=order_result['data'])
    return jsonify({"chargers": [iot_charger.json() for iot_charger in iot_charger_list]})


# @charging_station_bp.route("/nearby-chargers", methods=['GET'])
# def get_nearby_chargers():
#     print(request.args)
#     try:
#         # Get latitude and longitude from the request
#         lat_str = request.args.get('lat')
#         lon_str = request.args.get('lon')
#         print(lat_str, lon_str)
#         if lat_str is None or lon_str is None:
#             raise ValueError("Latitude and longitude are required.")

#         lat = float(lat_str)
#         lon = float(lon_str)
#         radius = float(request.args.get('radius', 10.0))  # Default radius is 10 kilometers

#         # Query nearby chargers using geopy
#         chargers = ChargingStation.query.all()
#         nearby_chargers = []

#         for charger in chargers:
#             if charger.latitude is not None and charger.longitude is not None:
#                 charger_coords = (charger.latitude, charger.longitude)
#                 user_coords = (lat, lon)

#                 distance = geodesic(user_coords, charger_coords).kilometers

#                 if distance <= radius:
#                     nearby_chargers.append({
#                         'charger_id': charger.charger_id,
#                         'charger_name': charger.charger_name,
#                         'latitude': charger.latitude,
#                         'longitude': charger.longitude,
#                         'distance': distance,
#                         'status': charger.status
#                     })

#         return jsonify({'nearby_chargers': nearby_chargers})

#     except ValueError as ve:
#         return jsonify({'error': str(ve)}), 400
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
