from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class IotCharger(db.Model):
    __tablename__ = 'iotcharger'

    iot_charger_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(15), nullable=False, default='Disconnected')
    charger_id = db.Column(db.Integer, nullable=False) #foreign key?
    
    def json(self):
        dto = {
            'iot_charger_id': self.iot_charger_id,
            'status': self.status,
            'charger_id': self.charger_id
        }

        return dto