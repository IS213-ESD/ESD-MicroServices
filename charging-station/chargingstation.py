#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from os import environ
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from datetime import datetime

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:R00t+@localhost:3306/chargingstationdb'
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class ChargingStation(db.Model):
    __tablename__ = 'chargingstation'

    charger_id = db.Column(db.Integer, primary_key=True)
    charger_name = db.Column(db.String(30), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='UP')
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def json(self):
        dto = {
            'charger_id': self.charger_id,
            'charger_name': self.charger_name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S"),  # format the datetime
            'modified': self.modified.strftime("%Y-%m-%d %H:%M:%S")  # format the datetime
        }

        return dto


@app.route("/chargers")
def get_all_chargers():
    try:
        db.session.commit()
        charger_list = ChargingStation.query.all()
        chargers = [charger.json() for charger in charger_list]

        if chargers:
            return jsonify(
                {
                    "code": 200,
                    "data": {
                        "chargers": chargers
                    }
                }
            )
        else:
            return "No chargers found in the database."
    except Exception as e:
        return f"Error: {str(e)}"


def insert_dummy_charger():
    try:
        dummy_charger = ChargingStation(
            charger_name='Dummy Charger',
            latitude=41.7128,
            longitude=-74.0060,
            status='UP'
        )
        db.session.add(dummy_charger)
        db.session.commit()
        print("Dummy charger inserted successfully.")
    except Exception as e:
        print(f"Error inserting dummy charger: {str(e)}")
        db.session.rollback()

@app.route("/insert_dummy_charger")
def route_insert_dummy_charger():
    insert_dummy_charger()
    return "Dummy charger insertion triggered."


# @app.route("/chargers")
# def get_all_chargers():
#     charger_list = db.session.query(ChargingStation).all()
#     print(charger_list)
#     if charger_list:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": {
#                     "chargers": [charger.json() for charger in charger_list]
#                 }
#             }
#         )
#
#     return jsonify(
#         {
#             "code": 404,
#             "message": "There are no charging stations."
#         }
#     ), 404


# class Order(db.Model):
#     __tablename__ = 'chargingstation'

#     order_id = db.Column(db.Integer, primary_key=True)
#     customer_id = db.Column(db.String(32), nullable=False)
#     status = db.Column(db.String(10), nullable=False)
#     created = db.Column(db.DateTime, nullable=False, default=datetime.now)
#     modified = db.Column(db.DateTime, nullable=False,
#                          default=datetime.now, onupdate=datetime.now)

#     def json(self):
#         dto = {
#             'order_id': self.order_id,
#             'customer_id': self.customer_id,
#             'status': self.status,
#             'created': self.created,
#             'modified': self.modified
#         }

#         dto['order_item'] = []
#         for oi in self.order_item:
#             dto['order_item'].append(oi.json())

#         return dto


# class Order_Item(db.Model):
#     __tablename__ = 'order_item'

#     item_id = db.Column(db.Integer, primary_key=True)
#     order_id = db.Column(db.ForeignKey(
#         'order.order_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

#     book_id = db.Column(db.String(13), nullable=False)
#     quantity = db.Column(db.Integer, nullable=False)

#     # order_id = db.Column(db.String(36), db.ForeignKey('order.order_id'), nullable=False)
#     # order = db.relationship('Order', backref='order_item')
#     order = db.relationship(
#         'Order', primaryjoin='Order_Item.order_id == Order.order_id', backref='order_item')

#     def json(self):
#         return {'item_id': self.item_id, 'book_id': self.book_id, 'quantity': self.quantity, 'order_id': self.order_id}


# @app.route("/chargers")
# def get_all():
#     orderlist = db.session.scalars(db.select(Order)).all()
#     if len(orderlist):
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": {
#                     "orders": [order.json() for order in orderlist]
#                 }
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#             "message": "There are no orders."
#         }
#     ), 404


# @app.route("/order/<string:order_id>")
# def find_by_order_id(order_id):
#     order = db.session.scalars(
#         db.select(Order).filter_by(order_id=order_id).limit(1)).first()
#     if order:
#         return jsonify(
#             {
#                 "code": 200,
#                 "data": order.json()
#             }
#         )
#     return jsonify(
#         {
#             "code": 404,
#             "data": {
#                 "order_id": order_id
#             },
#             "message": "Order not found."
#         }
#     ), 404


# @app.route("/order", methods=['POST'])
# def create_order():
#     customer_id = request.json.get('customer_id', None)
#     order = Order(customer_id=customer_id, status='NEW')

#     cart_item = request.json.get('cart_item')
#     for item in cart_item:
#         order.order_item.append(Order_Item(
#             book_id=item['book_id'], quantity=item['quantity']))

#     try:
#         db.session.add(order)
#         db.session.commit()
#     except Exception as e:
#         return jsonify(
#             {
#                 "code": 500,
#                 "message": "An error occurred while creating the order. " + str(e)
#             }
#         ), 500

#     return jsonify(
#         {
#             "code": 201,
#             "data": order.json()
#         }
#     ), 201


# @app.route("/order/<string:order_id>", methods=['PUT'])
# def update_order(order_id):
#     try:
#         order = db.session.scalars(
#         db.select(Order).filter_by(order_id=order_id).
#         limit(1)).first()
#         if not order:
#             return jsonify(
#                 {
#                     "code": 404,
#                     "data": {
#                         "order_id": order_id
#                     },
#                     "message": "Order not found."
#                 }
#             ), 404

#         # update status
#         data = request.get_json()
#         if data['status']:
#             order.status = data['status']
#             db.session.commit()
#             return jsonify(
#                 {
#                     "code": 200,
#                     "data": order.json()
#                 }
#             ), 200
#     except Exception as e:
#         return jsonify(
#             {
#                 "code": 500,
#                 "data": {
#                     "order_id": order_id
#                 },
#                 "message": "An error occurred while updating the order. " + str(e)
#             }
#         ), 500


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
