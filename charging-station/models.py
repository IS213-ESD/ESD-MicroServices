from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

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
    
    
class ChargingStationBooking(db.Model):
    __tablename__ = 'chargingstationbooking'

    booking_id = db.Column(db.Integer, primary_key=True)
    charger_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time_start = db.Column(db.Time, nullable=False)
    booking_duration_hours = db.Column(db.Integer, nullable=False)
    booking_status = db.Column(db.Enum('IN_PROGRESS', 'CANCELLED', 'COMPLETED', 'EXCEEDED'), default='IN_PROGRESS')

    def json(self):
        dto = {
            'booking_id': self.booking_id,
            'charger_id': self.charger_id,
            'user_id': self.user_id,
            'booking_date': self.booking_date.strftime('%Y-%m-%d'),
            'booking_time_start': self.booking_time_start.strftime('%H:%M:%S'),
            'booking_duration_hours': self.booking_duration_hours,
            'booking_status': self.booking_status
        }

        return dto