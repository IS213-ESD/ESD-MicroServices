from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import base64

db = SQLAlchemy()

class ChargingStation(db.Model):
    __tablename__ = 'chargingstation'

    charger_id = db.Column(db.Integer, primary_key=True)
    charger_name = db.Column(db.String(30), nullable=False)
    charger_location = db.Column(db.String(100), nullable=False)
    charger_image = db.Column(db.Text, nullable=True)  # Base64 image
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(10), nullable=False, default='UP')
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    charging_status = db.Column(db.String(20), nullable=False, default='Not Charging')
    def json(self):
        dto = {
            'charger_id': self.charger_id,
            'charger_name': self.charger_name,
            'charger_location': self.charger_location,
            'charger_image': self.charger_image,  # Include charger image
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'created': self.created.strftime("%Y-%m-%d %H:%M:%S"),  # format the datetime
            'modified': self.modified.strftime("%Y-%m-%d %H:%M:%S"),  # format the datetime
            'charging_status': self.charging_status
        }
        return dto
    
    
class ChargingStationBooking(db.Model):
    __tablename__ = 'chargingstationbooking'

    booking_id = db.Column(db.Integer, primary_key=True)
    charger_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(30), nullable=False)
    booking_datetime = db.Column(db.DateTime, nullable=False) 
    booking_duration_hours = db.Column(db.Integer, nullable=False)
    booking_status = db.Column(db.Enum('IN_PROGRESS', 'CANCELLED', 'COMPLETED', 'EXCEEDED', 'PENDING'), default='PENDING')
    payment_id = db.Column(db.Integer, nullable=False)
    booking_fee = db.Column(db.Numeric(10, 2), default=0)  # New field for booking fee
    charging_fee = db.Column(db.Numeric(10, 2), default=0)  # New field for charging fee
    notification_before = db.Column(db.Boolean, default=False)  # New field for notification_before
    notification_after = db.Column(db.Boolean, default=False)   # New field for notification_after
    def json(self):
        dto = {
            'booking_id': self.booking_id,
            'charger_id': self.charger_id,
            'user_id': self.user_id,
            'booking_datetime': self.booking_datetime,
            'booking_duration_hours': self.booking_duration_hours,
            'booking_status': self.booking_status,
            'payment_id': self.payment_id,
            'booking_fee': self.booking_fee,
            'charging_fee': self.charging_fee,
            'notification_before': self.notification_before,
            'notification_after': self.notification_after
        }

        return dto