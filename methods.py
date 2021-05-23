import random
from datetime import datetime
from typing import Optional, List

import pytz

from app import login
from config import Config
from errors import PlayerInRegionNot16, PlayerInGroupNot48
from models import User, Group, Player, Match


def create_groups(season: str, week: int) -> None:
    if not (1 <= week <= 7):
        return
    group: Group = Group.objects.filter_by(season=season, week=week).first()
    if group:
        return
    players: List[Player] = Player.objects.filter_by(season=season).get()
    players_to_create: List[Group] = list()
    for region in Config.REGIONS:
        region_players = [player for player in players if player.region == region]
        if len(region_players) != 4 * 4:
            raise PlayerInRegionNot16(region_players)
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


def create_initial_matches(season: str, week: int) -> None:
    if not (1 <= week <= 7):
        return
    match: Match = Match.objects.filter_by(season=season, week=week).first()
    if match:
        return
    groups: List[Group] = Group.objects.filter_by(season=season, week=week).get()
    if len(groups) != 4 * 4 * 3:
        raise PlayerInGroupNot48(groups)
    matches_to_create: List[Match] = list()
    match_index = 1
    for region in Config.REGIONS:
        region_players = [player for player in groups if player.region == region]
        for group_index in range(0, 4):
            group_players = [player for player in region_players if player.group == Config.GROUPS[group_index]]
            for player_index in range(0, 3, 2):
                order_index = int(player_index / 2)
                match = Match()
                match.season = season
                match.week = week
                match.region = region
                match.group = Config.GROUPS[group_index]
                match.order = order_index + 1
                match.type = Config.MATCH_TYPES[order_index]
                match.player1 = group_players[player_index].player
                match.player2 = group_players[player_index + 1].player
                match.match_id = f"{Config.SEASON2021_1_TAG}-{match_index:003}"
                match_index += 1
                matches_to_create.append(match)
    Match.objects.create_all(Match.objects.to_dicts(matches_to_create))


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
