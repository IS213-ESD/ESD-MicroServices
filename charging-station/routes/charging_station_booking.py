from flask import Flask, request, jsonify, Blueprint, jsonify
from models import ChargingStationBooking

charging_station_booking_bp = Blueprint('charging_station_booking', __name__)

@charging_station_booking_bp.route("/bookings")
def get_all_bookings():
    booking_list = ChargingStationBooking.query.all()
    return jsonify({"bookings": [booking.json() for booking in booking_list]})