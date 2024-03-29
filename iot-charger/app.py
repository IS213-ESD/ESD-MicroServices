import os
from flask import Flask
from config import Config
from models import db
from celery_utils import make_celery
from routes.iot_charger import iot_charger_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(iot_charger_bp)

# Initialize Celery
celery = make_celery(app)

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5003, debug=True)