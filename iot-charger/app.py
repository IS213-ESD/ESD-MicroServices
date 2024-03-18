import os
from flask import Flask
from config import Config
from models import db
from routes.iot_charger import iot_charger_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(iot_charger_bp)

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5002, debug=True)