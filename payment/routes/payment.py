from flask import Flask, request, jsonify, Blueprint, jsonify
from models import Payment, db
from sqlalchemy import text, func


payment_bp = Blueprint('payment', __name__)

@payment.route("/payments")
def get_all_payments():
    iot_charger_list = IotCharger.query.all()
    return jsonify({"chargers": [iot_charger.json() for iot_charger in iot_charger_list]})

@payment.route("/payment-status/<string:isbn13>")
def find_by_isbn13(isbn13):
    book = db.session.scalars(
        db.select(Book).filter_by(isbn13=isbn13).
        limit(1)
).first()

    if book:
        return jsonify(
            {
                "code": 200,
                "data": book.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Book not found."
        }
    ), 404


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
