import os
from flask import Flask

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"


app = Flask(__name__)

if __name__ == "__main__":
    app.run()

# noinspection PyUnresolvedReferences
from routes import *
