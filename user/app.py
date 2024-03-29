import os
from flask import Flask
from config import Config
from models import db
from routes.users import users_bp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(users_bp)


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage users ...")
    app.run(host='0.0.0.0', port=5001, debug=True)

