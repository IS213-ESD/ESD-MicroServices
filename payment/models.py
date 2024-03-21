from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True)
    stripe_id = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Use Float for floating point numbers
    status = db.Column(db.String(20), nullable=False, default='incomplete')
    # transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    # booking id
    # customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    
    def json(self):
        dto = {
            'payment_id': self.payment_id,
            'stripe_id' : self.stripe_id,
            'amount': self.amount,
            'status': self.status,
        }

        return dto

