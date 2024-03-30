import os
from flask import Flask
from routes.usernotification import notif_bp
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.register_blueprint(notif_bp)


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": send notifications to user ...")
    app.run(host='0.0.0.0', port=5001, debug=True)

