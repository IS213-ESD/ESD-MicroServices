from flask import request, jsonify, Blueprint, jsonify
from models import User
from models import db
from firebaseconfig import auth


users_bp = Blueprint('users', __name__)
# Sign-up endpoint
@users_bp.route("/signup", methods=["POST"])
def signup():
    try:
        # Get user registration data from request body
        data = request.json
        required_fields = ["email", "password", "phone"]
        # Check if all required fields are present
        if not all(field in data for field in required_fields):
            return jsonify({"message": "Missing required fields"}), 400
        else:
            email = data["email"]
            password = data["password"]
            phone = data["phone"]
            # Create user account in Firebase Authentication
            user = auth.create_user_with_email_and_password(
                email=email,
                password=password
            )
            if user:
                new_user = User(
                    user_id = user['localId'],
                    email=email,
                    phone=phone
                )
        
                # Add user to database
                db.session.add(new_user)
                db.session.commit()
                # Return success response with user ID token
                return jsonify({
                    'code': 200,
                    'message': 'User registered successfully', 
                    'user_id': new_user.user_id}), 200

    except Exception as e:
        # Return error response
        return jsonify({
            "code": 400,
            "message": "User creation failed"
        }), 400


# Sign-in endpoint
@users_bp.route("/signin", methods=["POST"])
def signin():
    try:
        # Get user login credentials from request body
        data = request.json
        email = data["email"]
        password = data["password"]

        # Sign in user with Firebase Authentication
        user = auth.sign_in_with_email_and_password(email, password)

        # Return success response with user ID token
        return jsonify({
            "code": 200, 
            "message": "User signed in successfully", 
            'user_id': user['localId']}
        ), 200
    except Exception as e:
        # Return error response
        return jsonify({
            "code": 400,
            "message": "User Login Failed"
        }), 400


# Update User Details in Profile Page endpoint
@users_bp.route("/userdetails", methods=["POST"])
def updateuserdetails():
    data = request.json
    try:
        user_id = data['user_id']
        homeaddress = data["homeaddress"]
        phone = data["phone"]
        username = data["username"]
        # Query the database to find the user with the specified user_id
        user = User.query.filter_by(user_id=user_id).first()
        # If user exists, update their attributes
        if user:
            user.homeaddress = homeaddress
            user.phone = phone
            user.username = username
            
            # Commit the changes to the database
            db.session.commit()
            # Return success response with user ID token
            return jsonify({
                "code": 200,
                "message": "User details updated successfully", 
                "user_id": user_id}
            ), 200
        else:
            # Return error response
            return jsonify({
                "code": 400,
                "message": "User Details Update failed"}
            ), 400
    except Exception as e:
        # Return error response
        return jsonify({
            "code": 400,
            "message": "User Details Update failed"
        }), 400


# GET User Details endpoint
@users_bp.route("/getuserdetails/<string:user_id>", methods=["GET"])
def getuserdetails(user_id):
    # Query the database to find the user with the specified user_id
    user = User.query.filter_by(user_id=user_id).first()
    # If user exists, get the specified attributes
    if user:
        email = user.email
        homeaddress = user.homeaddress
        phone = user.phone
        username = user.username
        # Return success response with specified attributes
        return jsonify({
            "code": 200,
            "message": "User Details retrieved successfully", 
            "user_id": user_id,
            "email": email, 
            "homeaddress": homeaddress,
            "phone": phone,
            "username": username
        }), 200
    else:
        # Return error response
        return jsonify({
            "code": 400,
            "message": "Invalid user",
        }), 400


# Payment Details endpoint (Profile page, receive token from Stripe checkout)
@users_bp.route("/paymentdetails", methods=["POST"])
def updatepayment():
    try:
        data = request.json
        user_id = data['user_id']
        payment_token = data['token']['id']
        if (payment_token == "") or (payment_token is None):
            return jsonify({
                "code": 400,
                "message": 'Payment Details Update failed'}
            ), 400
        # Query the database to find the user with the specified user_id
        user = User.query.filter_by(user_id=user_id).first()
        # If user exists, get payment token
        if user: 
            user.payment_token = payment_token
            db.session.commit()
            return jsonify({
                "code": 200,
                "message": "Payment Details updated successfully", 
            }), 200
    # Return error response
    except Exception as e:
        return jsonify({
            "code": 400,
            "message": 'Payment Details Update failed',
        }), 400


# GET Payment Details endpoint
@users_bp.route("/getpaymentdetails/<string:user_id>", methods=["GET"])
def getpaymentdetails(user_id):
    try:
        # Query the database to find the user with the specified user_id
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            payment_token = user.payment_token
            if payment_token:
                # If payment_token is not empty and user exists, return payment token
                return jsonify({
                    "code": 200,
                    "message": "Payment Details retrieved successfully", 
                    "user_id": user_id,
                    "payment_token": payment_token
                }), 200
            else:
                # Check if payment_token is empty, if yes return error response for user to update payment details in profile page
                return jsonify({
                    "code": 400,
                    "message": "Retrieval of Payment Details failed. Please ensure Payment Details are added at Profile Page."
                }), 400
    # Return error response
    except Exception as e:
        return jsonify({
            "code": 400,
            "message": "Retrieval of Payment Details failed. Please ensure Payment Details are added at Profile Page."
        }), 400


# GET all users endpoint
@users_bp.route("/getusers")
def getusers():
    user_list = User.query.all()
    return jsonify({"users": [user.json() for user in user_list]})

