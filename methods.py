from datetime import datetime
from typing import Optional

import pytz

from app import login
from models import User

@login.user_loader
def load_user(username: str) -> Optional[User]:
    user: User = User.objects.filter_by(username=username.lower()).first()
    return user


def check_token(token: str) -> Optional[User]:
    if not token:
        return None
    user: User = User.objects.filter_by(username=token).first()
    if user is None or user.token_expiration < datetime.utcnow().replace(tzinfo=pytz.UTC):
        return None
    return user

