from flask import Flask
from celery import Celery
import os

def make_celery(app):
    # Instantiate Celery object
    celery = Celery(
        app.import_name,
        broker=os.getenv("rabbitMQ")
    )
    celery.conf.update(app.config)

    # Ensure task execution uses Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    # create and configure the app
    app = Flask(__name__)

    # Load configurations from a configuration file or environment variables
    app.config.from_pyfile('config.py', silent=True)  # or os.environ['...']

    # Initialize Celery
    celery = make_celery(app)

    return app, celery

flask_app, celery = create_app()

# Import the tasks at the end to ensure they are discovered
from tasks import *

if __name__ == '__main__':
    celery.worker_main()
