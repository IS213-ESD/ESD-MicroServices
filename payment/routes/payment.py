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
        # Create a payment intent with Stripe
        payment_intent = stripe.PaymentIntent.create(
            amount=data['amount'],
            currency='sgd',
            payment_method="pm_card_visa",
            confirm=True,  
            automatic_payment_methods={
                'enabled': True,
                'allow_redirects': 'never'
        }
        )

        # Check if the payment intent was successfully confirmed
        if payment_intent.status == 'succeeded':
            # Save the payment details to your database
            new_payment = Payment(
                stripe_id=payment_intent['id'],
                amount=(data['amount']/100),
                status='complete'
            )
            db.session.add(new_payment)
            db.session.commit()

            # return jsonify({"message": "Payment successful", "payment_id": new_payment.payment_id}), 200
            return jsonify({"message": "Payment successful", "status": new_payment.payment_id}), 200
        else:
            new_payment = Payment(
                stripe_id=payment_intent['id'],
                amount=(data['amount']/100),
            )
            db.session.add(new_payment)
            db.session.commit()
            return jsonify({"message": "Payment confirmation failed", "status": payment_intent.status}), 400

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    
@payment_bp.route("/create-refund", methods=['POST'])
def create_refund():
    data = request.get_json()
    payment = Payment.query.filter_by(payment_id=data['payment_id']).first()
    if data and payment.status == 'complete':
        try:
        # Create a payment with Stripe
            refund = stripe.Refund.create(
                payment_intent=payment.stripe_id,
                amount=int((payment.amount * 100) * 0.3)
            )

            payment.status = 'refunded'
            db.session.commit()

            return jsonify({"message": "Refund successful"}), 200

        except Exception as e:
            return jsonify({"message": str(e)}), 500
    else:
        return jsonify({"message": 'Payment not completed or not found'}), 500
    
