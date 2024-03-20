import os
from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("dbURL") + "iotchargerdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 299}
    DEBUG = True
    CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672/'
    CELERY_RESULT_BACKEND = 'rpc://'