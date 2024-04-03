import os
from flask import Flask
from flask_cors import CORS

from config import Config
from routes.handle_late_collection import handle_late_collection_bp


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config.from_object(Config)

app.register_blueprint(handle_late_collection_bp)


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage late collections ...")
    app.run(host='0.0.0.0', port=5105, debug=True)