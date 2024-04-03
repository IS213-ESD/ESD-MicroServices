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

# will take in card details and create a payment method that can be used for future payments
@payment_bp.route('/create-payment-method', methods=['POST'])
def create_payment_method():
    try:
        data = request.get_json()
        # return jsonify({"payment_method_id": customer_obj}), 200
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "number": data['number'],
                "exp_month": data['exp_month'],
                "exp_year": data['exp_year'],
                "cvc": data['cvc'],
            },
        )
        customer_obj = stripe.Customer.create(
            name="doesntmatterwho",
            email="doesntmatterwho@idc.com",
            payment_method=payment_method.id
        )
        return jsonify({"payment_method_id": f'{customer_obj.id}:{payment_method.id}'}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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

# takes in payment method and amount to post payment to stripe
@payment_bp.route("/create-payment", methods=['POST'])
def create_payment():
    data = request.get_json()
    charge_amount = int(float(data['amount']) * 100)
    try:
        # Create a payment intent with Stripe
        stripe_customer_id, stripe_payment_id = data['payment_method_id'].split(":")
        payment_intent = stripe.PaymentIntent.create(
            amount=charge_amount,
            currency='sgd',
            payment_method=stripe_payment_id,
            customer=stripe_customer_id,
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
                amount=(charge_amount),
                status='complete'
            )
            db.session.add(new_payment)
            db.session.commit()

            # return jsonify({"message": "Payment successful", "payment_id": new_payment.payment_id}), 200
            return jsonify({"message": "Payment successful", "status": new_payment.payment_id}), 200
        else:
            new_payment = Payment(
                stripe_id=payment_intent['id'],
                amount=(charge_amount),
            )
            db.session.add(new_payment)
            db.session.commit()
            return jsonify({"message": "Payment confirmation failed", "status": payment_intent.status}), 400

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# takes in payment_id to create refund from stripe
@payment_bp.route("/create-refund", methods=['POST'])
def create_refund():
    data = request.get_json()
    payment = Payment.query.filter_by(payment_id=data['payment_id']).first()
    if data and payment.status == 'complete':
        try:
        # Create a refund with Stripe
            refund = stripe.Refund.create(
                payment_intent=payment.stripe_id,
                amount=int((payment.amount * 100) * 0.7)
            )

            payment.status = 'refunded'
            db.session.commit()

            return jsonify({"message": "Refund successful"}), 200

        except Exception as e:
            return jsonify({"message": str(e)}), 500
    else:
        return jsonify({"message": 'Payment not completed or not found'}), 500
    
