from flask import Flask
from flask_cors import CORS
from routes.book_charger import book_charger_bp

app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(book_charger_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
