from flask import Flask, request, jsonify, Blueprint, jsonify, send_from_directory
from models import ChargingStation, ChargingStationBooking, db
from sqlalchemy import text, func
import datetime
from geopy.distance import geodesic


charging_station_bp = Blueprint('charging_station', __name__, url_prefix='/charging-station')


@charging_station_bp.route('/images/<image_filename>')
def get_charger_image(image_filename):
    # Replace 'charger_images' with the path to your directory containing charger images
    directory = 'images'
    return send_from_directory(directory, image_filename)


@charging_station_bp.route("/chargers")
def get_all_chargers():
    charger_list = ChargingStation.query.all()
    return jsonify({"chargers": [charger.json() for charger in charger_list]})


@charging_station_bp.route("/nearby-chargers", methods=['GET'])
def get_nearby_chargers():
    print(request.args)
    try:
        # Get latitude and longitude from the request
        lat_str = request.args.get('lat')
        lon_str = request.args.get('lon')
        print(lat_str, lon_str)
        if lat_str is None or lon_str is None:
            raise ValueError("Latitude and longitude are required.")

        lat = float(lat_str)
        lon = float(lon_str)
        radius = float(request.args.get('radius', 10.0))  # Default radius is 10 kilometers

        # Query nearby chargers using geopy
        chargers = ChargingStation.query.all()
        nearby_chargers = []

        for charger in chargers:
            if charger.latitude is not None and charger.longitude is not None:
                charger_coords = (charger.latitude, charger.longitude)
                user_coords = (lat, lon)

                distance = geodesic(user_coords, charger_coords).kilometers

                if distance <= radius:
                    nearby_chargers.append(charger.json())
        return jsonify({'nearby_chargers': nearby_chargers})

    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@charging_station_bp.route("/nearby_stations_booking", methods=['GET'])
def get_nearby_stations():
    try:
        # Extract parameters from the request
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius'))
        booking_date = request.args.get('booking_date')  # format: 'YYYY-MM-DD'
        booking_time = request.args.get('booking_time')  # format: 'HH:mm:ss'
        booking_datetime = datetime.datetime.strptime(booking_date + ' ' + booking_time, '%Y-%m-%d %H:%M:%S')
        booking_duration = int(request.args.get('booking_duration'))
        available_stations = ChargingStation.query.filter(
        ~ChargingStation.charger_id.in_(
                db.session.query(ChargingStationBooking.charger_id).filter(
                    func.check_booking_overlap(ChargingStationBooking.charger_id, 
                    booking_datetime,
                    booking_duration)
                )
            )
        ).all()
        # Filter by location
        nearby_stations = []
        for charger in available_stations:
            if charger.latitude is not None and charger.longitude is not None:
                charger_coords = (charger.latitude, charger.longitude)
                user_coords = (lat, lon)

                distance = geodesic(user_coords, charger_coords).kilometers

                if distance <= radius:
                    nearby_stations.append(charger.json())
        return jsonify({"code": 200, "data": {"nearby_stations": nearby_stations}})
    except Exception as e:
        return jsonify({"code": 500, "message": f"Error: {str(e)}"}), 500