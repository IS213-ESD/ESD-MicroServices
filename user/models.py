from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.String(30), primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    homeaddress = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(8), nullable=True)
    username = db.Column(db.String(30), nullable=True)
    payment_token = db.Column(db.String(50), nullable=True)





    def json(self):
        dto = {
            'user_id': self.user_id,
            'email': self.email,
            'homeaddress': self.homeaddress,
            'phone': self.phone,
            'username': self.username,
            'payment_token': self.payment_token
        }

        return dto