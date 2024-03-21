from celery import Celery
import os

def make_celery(app):
    # Configure Celery
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
