import os
from flask import Flask
from flask_cors import CORS

from config import Config
from models import db
from routes.handle_bookings import handle_booking_bp


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(handle_booking_bp)


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5011, debug=True)