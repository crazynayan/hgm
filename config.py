import os
from base64 import b64encode
from typing import List


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or b64encode(os.urandom(24)).decode()
    CI_SECURITY = True if os.environ.get("ENVIRONMENT") == "prod" else False
    SESSION_COOKIE_SECURE = CI_SECURITY
    TOKEN_EXPIRY = 3600  # 1 hour = 3600 seconds
    # Game related
    APAC, EUROPE, AMERICAS = "Asia-Pacific", "Europe", "Americas"
    REGIONS = (APAC, EUROPE, AMERICAS)
    SEASON2021_1 = "2021 Season 1"


def _add_players(player_list: List[str], region: str) -> None:
    players: list = list()
    from models import Player
    for name in player_list:
        player: Player = Player()
        player.name = name
        player.region = region
        player.season = Config.SEASON2021_1
        players.append(player)
    Player.objects.create_all(Player.objects.to_dicts(players))


def add_apac_players():
    apac = ["tom60229", "Bankyugi", "blitzchung", "che0nsu", "Posesi", "Shaxy", "Hi3", "lambyseries",
            "Alan870806", "Alutemu", "DawN", "Surrender", "TIZS", "glory", "Tyler", "GivePLZ"]
    _add_players(apac, Config.APAC)


def add_america_players():
    america = ["Rami94", "Tincho", "Eddie", "Fr0zen", "killinallday", "lnguagehackr", "Monsanto", "Firebat",
               "NoHandsGamer", "Impact", "DreadEye", "Nalguidan", "Fled", "muzzy", "lunaloveee", "Briarthorn"]
    _add_players(america, Config.AMERICAS)


def add_europe_players():
    europe = ["Bozzzton", "Rdu", "Seiko", "Bunnyhoppor", "xBlyzes", "Warma", "AyRoK", "Frenetic", "Thijs",
              "Zhym", "Leta", "Viper", "Casie", "Felkeine", "Swidz", "Jarla"]
    _add_players(europe, Config.EUROPE)
