import pyrebase
from collections.abc import MutableMapping
import os
from dotenv import load_dotenv

load_dotenv()

firebaseConfig = {
  'apiKey': os.getenv("FIREBASE_API"),
  'authDomain': os.getenv("AUTHDOMAIN"),
  'projectId': os.getenv("PROJECTID"),
  'storageBucket': os.getenv("STORAGEBUCKET"),
  'messagingSenderId': os.getenv("MESSAGINGSENDERID"),
  'appId': os.getenv("APPID"),
  'databaseURL': ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()