from flask import Flask, request, jsonify, Blueprint, jsonify
from models import Payment, db
from sqlalchemy import text, func
import stripe
import os

payment_bp = Blueprint('payment', __name__)

stripe.api_key = os.getenv('STRIPE_API_KEY')

@payment_bp.route("/payments")
def get_all_payments():
    payment_list = Payment.query.all()
    return jsonify({"payments": [payment.json() for payment in payment_list]})

@payment_bp.route("/payment-status/<int:payment_id>")
def find_by_id(payment_id):
    payment = Payment.query.filter_by(payment_id=payment_id).first()

    if payment:
        return jsonify(
            {
                "code": 200,
                "data": payment.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Payment not found."
        }
    ), 404

@payment_bp.route("/create-payment", methods=['POST'])
def create_payment():
    data = request.get_json()
    try:
        # Create a payment with Stripe
        payment = stripe.PaymentIntent.create(
            amount=data['amount'],
            currency='sgd',
            payment_method="pm_card_visa"
        )

        # Save the payment details to your database
        new_payment = Payment(
            amount=data['amount'],
            is_successful=True  # Assuming the payment is successful if it reaches this point
        )
        db.session.add(new_payment)
        db.session.commit()

        return jsonify({"message": "Payment successful", "payment_id": new_payment.payment_id}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    
@payment_bp.route("/create-refund", methods=['POST'])
def create_refund():
    data = request.get_json()
    try:
        # Create a payment with Stripe
        refund = stripe.PaymentIntent.create(
            payment_intent=data['payment_id'],
            amount=data['amount']
        )

        # # Save the payment details to your database
        # new_payment = Payment(
        #     amount=data['amount'],
        #     is_successful=True  # Assuming the payment is successful if it reaches this point
        # )
        # db.session.add(new_payment)
        # db.session.commit()

        return jsonify({"message": "Refund successful"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


# funciton to post to call to stripe api
# @payment_bp.route("/payment-status/<int:payment_id>")
# def find_by_id(payment_id):
#     payment = Payment.query.filter_by(payment_id=payment_id).first()

#     if payment:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": payment.json()
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#             "message": "Payment not found."
#         }
#     ), 404



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
