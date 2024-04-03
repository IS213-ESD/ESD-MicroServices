import os
from flask import Flask
from flask_cors import CORS

from config import Config
from routes.handle_iot_chargers import handle_iot_chargers_bp


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)

app.register_blueprint(handle_iot_chargers_bp)


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5103, debug=True)