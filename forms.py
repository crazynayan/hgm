from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, RadioField
from wtforms.validators import InputRequired

from models import Match


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Sign In")


class MatchForm(FlaskForm):
    match_radio = RadioField("Select winner of the following match", choices=list())
    submit = SubmitField("Submit Winner")

    def __init__(self, match: Match, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.match_radio.choices.append((match.player1, match.player1))
        self.match_radio.choices.append((match.player2, match.player2))
