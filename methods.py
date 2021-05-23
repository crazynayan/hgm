import random
from datetime import datetime
from typing import Optional, List

import pytz

from app import login
from config import Config
from errors import CreateGroupsException
from models import User, Group, Player


def create_groups(season: str, week: int) -> None:
    if not (1 <= week <= 7):
        return
    groups: List[Group] = Group.objects.filter_by(season=season, week=week).first()
    if groups:
        return
    players: List[Player] = Player.objects.filter_by(season=season).get()
    players_to_create: List[Group] = list()
    for region in Config.REGIONS:
        region_players = [player for player in players if player.region == region]
        if len(region_players) != 16:
            raise CreateGroupsException(region_players)
        for group_index in range(0, 4):
            group_players = random.sample(region_players, k=4)
            region_players = [player for player in region_players if player not in group_players]
            for player in group_players:
                group_player = Group()
                group_player.player = player.name
                group_player.week = week
                group_player.season = season
                group_player.group = Config.GROUPS[group_index]
                group_player.region = player.region
                players_to_create.append(group_player)
    Group.objects.create_all(Group.objects.to_dicts(players_to_create))


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
