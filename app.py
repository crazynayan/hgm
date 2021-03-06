import os

from flask import Flask
from flask_login import LoginManager

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud.json"

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
login.login_view = "login"
login.session_protection = "strong" if Config.CI_SECURITY else "basic"


@app.shell_context_processor
def make_shell_context():
    from models import Player
    import methods
    return {
        "User": User,
        "Player": Player,
        "Config": Config,
        "methods": methods
    }


if __name__ == "__main__":
    app.run()

# noinspection PyUnresolvedReferences
from routes import *
