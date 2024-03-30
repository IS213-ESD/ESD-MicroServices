import os
from flask import Flask
from flask_cors import CORS


from config import Config
from models import db
from routes.charging_station import charging_station_bp
from routes.charging_station_booking import charging_station_booking_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(charging_station_bp)
app.register_blueprint(charging_station_booking_bp)


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5001, debug=True)