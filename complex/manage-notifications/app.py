from flask import Flask
from flask_cors import CORS
from routes.manage_notifications import manage_notifications_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(manage_notifications_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5103, debug=True)
