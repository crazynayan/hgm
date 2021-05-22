from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run()

# noinspection PyUnresolvedReferences
from routes import *
