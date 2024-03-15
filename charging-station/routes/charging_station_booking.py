from flask import Flask, request, jsonify, Blueprint, jsonify
from models import ChargingStationBooking, db
from sqlalchemy import text, func
import datetime

charging_station_booking_bp = Blueprint('charging_station_booking', __name__)

@charging_station_booking_bp.route("/charging-station-bookings")
def get_all_bookings():
    booking_list = ChargingStationBooking.query.all()
    return jsonify({"bookings": [booking.json() for booking in booking_list]})

@charging_station_booking_bp.route('/charging-station-bookings/<int:charger_id>', methods=['GET'])
def get_charging_station_bookings(charger_id):
    bookings = ChargingStationBooking.query.filter_by(charger_id=charger_id, booking_status="IN_PROGRESS").all()
    # Convert booking objects to JSON-compatible format
    bookings_json = [booking.json() for booking in bookings]
    # Return the JSON response
    return jsonify(bookings_json)


@charging_station_booking_bp.route('/bookings', methods=['POST'])
def create_booking():
    # Parse request data
    data = request.json
    charger_id = data.get('charger_id')
    user_id = data.get('user_id')
    booking_datetime = datetime.datetime.strptime(data.get('booking_datetime'), '%Y-%m-%d %H:%M:%S')
    booking_duration_hours = data.get('booking_duration_hours')
    
    # Check if slot is available for booking
    is_stations_available = db.session.query(func.check_booking_overlap(
        charger_id, 
        booking_datetime, 
        booking_duration_hours
    )).scalar()
    if is_stations_available:
        return jsonify({"code": 500, "error": "Booking overlap detected", 'message': 'Please choose another time.'}), 400
    
    # Create new booking
    new_booking = ChargingStationBooking(
        charger_id=charger_id,
        user_id=user_id,
        booking_datetime=booking_datetime,
        booking_duration_hours=booking_duration_hours,
        booking_status='IN_PROGRESS'
    )
    
    # # Add booking to database
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({'message': 'Booking created successfully', 'booking_id': new_booking.booking_id}), 201


@charging_station_booking_bp.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    # Get booking ID from request data
    booking_id = request.json.get('booking_id')

    # Check if booking ID is provided
    if not booking_id:
        return jsonify({'message': 'Booking ID is required'}), 400

    # Query the database for the booking
    booking = ChargingStationBooking.query.get(booking_id)

    # Check if the booking exists
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404

    # Update booking status to 'CANCELLED'
    booking.booking_status = 'CANCELLED'

    # Commit changes to the database
    db.session.commit()

    return jsonify({'message': 'Booking cancelled successfully'}), 200


@charging_station_booking_bp.route('/exceed_booking', methods=['POST'])
def exceed_booking():
    # Get booking ID from request data
    booking_id = request.json.get('booking_id')

    # Check if booking ID is provided
    if not booking_id:
        return jsonify({'message': 'Booking ID is required'}), 400

    # Query the database for the booking
    booking = ChargingStationBooking.query.get(booking_id)

    # Check if the booking exists
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404

    # Update booking status to 'CANCELLED'
    booking.booking_status = 'EXCEEDED'

    # Commit changes to the database
    db.session.commit()

    return jsonify({'message': 'Booking cancelled successfully'}), 200


@charging_station_booking_bp.route('/complete_booking', methods=['POST'])
def complete_booking():
    # Get booking ID from request data
    booking_id = request.json.get('booking_id')

    # Check if booking ID is provided
    if not booking_id:
        return jsonify({'message': 'Booking ID is required'}), 400

    # Query the database for the booking
    booking = ChargingStationBooking.query.get(booking_id)

    # Check if the booking exists
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404

    # Update booking status to 'CANCELLED'
    booking.booking_status = 'COMPLETED'

    # Commit changes to the database
    db.session.commit()

    return jsonify({'message': 'Booking cancelled successfully'}), 200