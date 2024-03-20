from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)  # Use Float for floating point numbers
    is_successful = db.Column(db.Boolean, default=False, nullable=False)  # Use Boolean for true/false
    # customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    # transaction_date = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)
    # booking id
    
    def json(self):
        dto = {
            'payment_id': self.payment_id,
            'amount': self.amount,
            'is_successful': self.is_successful,
        }

        return dto

