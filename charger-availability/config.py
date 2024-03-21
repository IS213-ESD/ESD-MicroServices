import os
from os import environ
from dotenv import load_dotenv

load_dotenv()

#includes databae settings and other configuration variables
#do i need to update my config.py: scheduling intervals for checks or API keys for sending notificaitons
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("dbURL") + "chargingstationdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 299}
    DEBUG = True