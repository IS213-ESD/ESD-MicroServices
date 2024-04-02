from flask import Flask, request, jsonify, Blueprint, jsonify
from models import ChargingStationBooking, db
from sqlalchemy import text, func
import datetime

charging_station_booking_bp = Blueprint('charging_station_booking', __name__, url_prefix='/charging-station-booking')

PRICE_PER_HOUR_BLOCK=10

@charging_station_booking_bp.route("/")
def get_all_bookings():
    booking_list = ChargingStationBooking.query.all()
    return jsonify({"bookings": [booking.json() for booking in booking_list]})

@charging_station_booking_bp.route('/charger/<int:charger_id>', methods=['GET'])
def get_charging_station_bookings_by_charger(charger_id):
    bookings = ChargingStationBooking.query.filter_by(charger_id=charger_id, booking_status="IN_PROGRESS").all()
    # Convert booking objects to JSON-compatible format
    bookings_json = [booking.json() for booking in bookings]
    # Return the JSON response
    return jsonify(bookings_json)

@charging_station_booking_bp.route('/user/<string:user_id>', methods=['GET'])
def get_charging_station_bookings_by_user(user_id):
    bookings = ChargingStationBooking.query.filter_by(user_id=user_id).all()
    # Convert booking objects to JSON-compatible format
    bookings_json = [booking.json() for booking in bookings]
    # Return the JSON response
    return jsonify(bookings_json)

@charging_station_booking_bp.route('/booking/<int:booking_id>', methods=['GET'])
def get_charging_station_bookings_by_booking(booking_id):
    booking = ChargingStationBooking.query.filter_by(booking_id=booking_id).first()
    # Convert booking objects to JSON-compatible format
    bookings_json = booking.json()
    # Return the JSON response
    return jsonify(bookings_json)

@charging_station_booking_bp.route('/create_booking', methods=['POST'])
def create_booking():
    # Parse request data
    data = request.json
    charger_id = data.get('charger_id')
    user_id = data.get('user_id')
    booking_datetime = datetime.datetime.strptime(data.get('booking_datetime'), '%Y-%m-%d %H:%M:%S')
    booking_duration_hours = data.get('booking_duration_hours')
    booking_status = data.get('booking_status', 'PENDING')
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
        booking_status=booking_status,
        booking_fee=booking_duration_hours*PRICE_PER_HOUR_BLOCK
    )
    
    # # Add booking to database
    db.session.add(new_booking)
    db.session.commit()
    
    return jsonify({'message': 'Booking created successfully', 'booking_id': new_booking.booking_id}), 201


@charging_station_booking_bp.route('/update_booking/<int:booking_id>', methods=['post'])
def update_booking(booking_id):
    # Parse request data
    data = request.json
    payment_id = data.get('payment_id')
    booking_status = "IN_PROGRESS"

    # Retrieve the booking from the database
    booking = ChargingStationBooking.query.get(booking_id)

    # Check if the booking exists
    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    # Update the booking with the new payment ID and booking status
    if payment_id:
        booking.payment_id = payment_id
    if booking_status:
        booking.booking_status = booking_status

    # Commit changes to the database
    db.session.commit()

    return jsonify({'message': 'Booking updated successfully', 'booking_id': booking_id}), 200


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

    return jsonify({'message': 'Booking status updated successfully'}), 200


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

    return jsonify({'message': 'Booking status updated successfully'}), 200


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

    return jsonify({'message': 'Booking status updated successfully'}), 200