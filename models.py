import os
from base64 import b64encode

import pytz
from datetime import datetime, timedelta

from flask_login import UserMixin
from firestore_ci import FirestoreDocument
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config


class User(FirestoreDocument, UserMixin):

    def __init__(self):
        super().__init__()
        self.username: str = str()
        self.password_hash: str = str()
        self.token: str = str()
        self.season: str = str()
        self.week: int = int()
        self.token_expiration: datetime = datetime.utcnow().replace(tzinfo=pytz.UTC)

    def __repr__(self) -> str:
        return f"{self.username}"

    def get_token(self, expires_in=Config.TOKEN_EXPIRY) -> str:
        now: datetime = datetime.utcnow().replace(tzinfo=pytz.UTC)
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token: str = b64encode(os.urandom(24)).decode()
        self.token_expiration: datetime = now + timedelta(seconds=expires_in)
        self.save()
        return self.token

    def revoke_token(self) -> None:
        self.token_expiration: datetime = datetime.utcnow() - timedelta(seconds=1)
        self.save()

    def set_password(self, password) -> None:
        self.password_hash: str = generate_password_hash(password)
        self.save()

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self) -> str:
        return self.username


User.init()


class Player(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = str()
        self.points: int = int()
        self.region: str = str()
        self.season: str = str()
        self.rank: int = int()

    def __repr__(self):
        return f"{self.name}:{self.region}:{self.points}"


Player().init()


class Match(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.season: str = str()
        self.region: str = str()
        self.week: int = int()
        self.group: str = str()
        self.type: str = str()
        self.player1: str = str()
        self.player2: str = str()
        self.winner: str = str()

    def __repr__(self):
        return f"{self.region}:{self.week}:{self.group}:{self.type}:{self.player1} v {self.player2}"

Match().init()


class Group(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.season: str = str()
        self.region: str = str()
        self.week: int = int()
        self.group: str = str()
        self.player: str = str()

    def __repr__(self):
        return f"{self.region}:{self.week}:{self.group}:{self.player}"


Group().init()
