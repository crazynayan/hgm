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
    SEASON2021_1_TAG = "GW2021-1"
    GROUP_A, GROUP_B, GROUP_C, GROUP_D = "Group A", "Group B", "Group C", "Group D"
    GROUPS = (GROUP_A, GROUP_B, GROUP_C, GROUP_D)
    INITIAL_1, INITIAL_2, QUALIFIER, ELIMINATOR = "Initial 1", "Initial 2", "Qualifier", "Eliminator"
    DECIDER, QUARTERFINAL_1, QUARTERFINAL_2 = "Decider", "Quarterfinal 1", "Quarterfinal 2"
    QUARTERFINAL_3, QUARTERFINAL_4 = "Quarterfinal 3", "Quarterfinal 4"
    SEMIFINAL_1, SEMIFINAL_2, FINAL = "Semifinal 1", "Semifinal 2", "Final"
    MATCH_TYPES = {
        INITIAL_1: 1,
        INITIAL_2: 2,
        QUALIFIER: 3,
        ELIMINATOR: 4,
        DECIDER: 5,
        QUARTERFINAL_1: 1,
        QUARTERFINAL_2: 2,
        QUARTERFINAL_3: 3,
        QUARTERFINAL_4: 4,
        SEMIFINAL_1: 1,
        SEMIFINAL_2: 2,
        FINAL: 3
    }
    QUARTERFINALS = (QUARTERFINAL_1, QUARTERFINAL_2, QUARTERFINAL_3, QUARTERFINAL_4)
    FINALS = (SEMIFINAL_1, SEMIFINAL_2, FINAL)
    TBD = "To Be Decided"


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
