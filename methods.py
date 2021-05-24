import random
from datetime import datetime
from typing import Optional, List

import pytz

from app import login
from config import Config
from errors import PlayerInRegionNot16, PlayerInGroupNot48
from models import User, Group, Player, Match


def update_standings(match: Match) -> None:
    players: List[Player] = Player.objects.filter_by(season=match.season, region=match.region).get()
    player = next(player for player in players if player.name == match.winner)
    player.points += 1
    players.sort(key=lambda item: (-item.points, item.name.upper()))
    for index, player in enumerate(players):
        player.rank = index + 1
    Player.objects.save_all(players)


def update_winner(match: Match, winner: str) -> None:
    match.winner = winner
    matches_to_update = [match]
    if match.type == Config.INITIAL_1:
        matches: List[Match] = _get_matches(match, Config.QUALIFIER, Config.ELIMINATOR)
        matches[0].player1 = match.winner
        matches[1].player1 = match.loser
        matches_to_update.extend(matches)
    elif match.type == Config.INITIAL_2:
        matches: List[Match] = _get_matches(match, Config.QUALIFIER, Config.ELIMINATOR)
        matches[0].player2 = match.winner
        matches[1].player2 = match.loser
        matches_to_update.extend(matches)
    elif match.type == Config.QUALIFIER:
        quarterfinal: Match = _get_match(match, Config.GROUP_TO_QUALIFIERS[match.group])
        decider: Match = _get_match_from_group(match, Config.DECIDER)
        quarterfinal.player1 = match.winner
        decider.player1 = match.loser
        matches_to_update.extend([quarterfinal, decider])
    elif match.type == Config.ELIMINATOR:
        decider: Match = _get_match_from_group(match, Config.DECIDER)
        decider.player2 = match.winner
        matches_to_update.append(decider)
    elif match.type == Config.DECIDER:
        quarterfinal: Match = _get_match(match, Config.GROUP_TO_DECIDERS[match.group])
        quarterfinal.player2 = match.winner
        matches_to_update.append(quarterfinal)
    elif match.type == Config.QUARTERFINAL_1:
        semifinal: Match = _get_match(match, Config.SEMIFINAL_1)
        semifinal.player1 = match.winner
        matches_to_update.append(semifinal)
    elif match.type == Config.QUARTERFINAL_2:
        semifinal: Match = _get_match(match, Config.SEMIFINAL_1)
        semifinal.player2 = match.winner
        matches_to_update.append(semifinal)
    elif match.type == Config.QUARTERFINAL_3:
        semifinal: Match = _get_match(match, Config.SEMIFINAL_2)
        semifinal.player1 = match.winner
        matches_to_update.append(semifinal)
    elif match.type == Config.QUARTERFINAL_4:
        semifinal: Match = _get_match(match, Config.SEMIFINAL_2)
        semifinal.player2 = match.winner
        matches_to_update.append(semifinal)
    elif match.type == Config.SEMIFINAL_1:
        final: Match = _get_match(match, Config.FINAL)
        final.player1 = match.winner
        matches_to_update.append(final)
    elif match.type == Config.SEMIFINAL_2:
        final: Match = _get_match(match, Config.FINAL)
        final.player2 = match.winner
        matches_to_update.append(final)
    Match.objects.save_all(matches_to_update)
    update_standings(match)


def _get_matches(match: Match, type1: str, type2: str) -> List[Match]:
    query = Match.objects.filter_by(season=match.season, week=match.week, region=match.region, group=match.group)
    matches: List[Match] = query.filter("type", Match.objects.IN, [type1, type2]).get()
    match_type1: Match = matches[0] if matches[0].type == type1 else matches[1]
    match_type2: Match = matches[0] if matches[0].type == type2 else matches[1]
    return [match_type1, match_type2]


def _get_match_from_group(match: Match, match_type: str) -> Match:
    query = Match.objects.filter_by(season=match.season, week=match.week, region=match.region, group=match.group)
    match_doc: Match = query.filter_by(type=match_type).first()
    return match_doc


def _get_match(match: Match, match_type: str) -> Match:
    query = Match.objects.filter_by(season=match.season, week=match.week, region=match.region)
    match_doc: Match = query.filter_by(type=match_type).first()
    return match_doc


def get_next_match(season: str, week: int) -> Match:
    match: Match = Match.objects.filter_by(season=season, week=week, winner=str()).order_by("match_id").first()
    return match


def prepare_for_next_week() -> None:
    user: User = User.objects.first()
    user.week += 1
    user.save()
    create_groups(user.season, user.week)
    create_initial_matches(user.season, user.week)
    create_tbd_matches(user.season, user.week)
    return


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
                match = Match()
                match.season = season
                match.week = week
                match.region = region
                match.group = Config.GROUPS[group_index]
                match.type = Config.INITIAL_1 if player_index == 0 else Config.INITIAL_2
                match.player1 = group_players[player_index].player
                match.player2 = group_players[player_index + 1].player
                match.match_id = _generate_match_id(match_index)
                match_index += 1
                matches_to_create.append(match)
    Match.objects.create_all(Match.objects.to_dicts(matches_to_create))


def create_tbd_matches(season: str, week: int) -> None:
    if not (1 <= week <= 7):
        return
    matches: List[Match] = Match.objects.filter_by(season=season, week=week).get()
    match_index = len(matches) + 1
    if match_index != 25:
        return
    matches_to_create: List[Match] = list()
    for region in Config.REGIONS:
        for group_index in range(0, 4):
            match = _create_tbd_match(season, week, region, Config.QUALIFIER, match_index, Config.GROUPS[group_index])
            matches_to_create.append(match)
            match_index += 1
            match = _create_tbd_match(season, week, region, Config.ELIMINATOR, match_index, Config.GROUPS[group_index])
            matches_to_create.append(match)
            match_index += 1
    for region in Config.REGIONS:
        for group_index in range(0, 4):
            match = _create_tbd_match(season, week, region, Config.DECIDER, match_index, Config.GROUPS[group_index])
            matches_to_create.append(match)
            match_index += 1
    for region in Config.REGIONS:
        for quarter_index in range(1, 5):
            match = _create_tbd_match(season, week, region, f"{Config.QUARTERFINAL_1[:-1]}{quarter_index}", match_index)
            matches_to_create.append(match)
            match_index += 1
    for region in Config.REGIONS:
        match = _create_tbd_match(season, week, region, Config.SEMIFINAL_1, match_index)
        matches_to_create.append(match)
        match_index += 1
        match = _create_tbd_match(season, week, region, Config.SEMIFINAL_2, match_index)
        matches_to_create.append(match)
        match_index += 1
        match = _create_tbd_match(season, week, region, Config.FINAL, match_index)
        matches_to_create.append(match)
        match_index += 1
    Match.objects.create_all(Match.objects.to_dicts(matches_to_create))


def _create_tbd_match(season: str, week: int, region: str, match_type: str, index: int, group: str = None) -> Match:
    match = Match()
    match.season = season
    match.week = week
    match.region = region
    match.type = match_type
    match.match_id = _generate_match_id(index)
    match.group = group if group else str()
    match.player1 = Config.TBD
    match.player2 = Config.TBD
    return match


def _generate_match_id(match_index: int) -> str:
    return f"{Config.SEASON2021_1_TAG}-{match_index:003}"


def reset_season(season: str):
    Group.objects.filter_by(season=season).delete()
    Match.objects.filter_by(season=season).delete()
    players = Player.objects.filter_by(season=season).get()
    for region in Config.REGIONS:
        region_players = [player for player in players if player.region == region]
        region_players.sort(key=lambda player: player.name.upper())
        for index, player in enumerate(region_players):
            player.rank = index + 1
            player.points = 0
    Player.objects.save_all(players)
    user = User.objects.first()
    user.week = 1
    user.season = season
    user.save()
    create_groups(season, 1)
    create_initial_matches(season, 1)
    create_tbd_matches(season, 1)
    print(f"{season} reset.")
    return


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
