from stormstats.models import *
from . import nhl
import json

def game_insert():
    return

def player_insert(player_dict:dict) -> Player:
    player = Player()
    player.player_id = player_dict["id"]
    player.name = player_dict["fullName"]
    player.jersey = player_dict["primaryNumber"]
    player.age = player_dict["currentAge"]
    player.height = player_dict["height"].replace('"', '')
    player.weight = player_dict["weight"]
    player.group = player_dict["primaryPosition"]["type"]
    player.position = player_dict["primaryPosition"]["name"]
    if ("birthStateProvince" in player_dict):
        player.birthplace = player_dict["birthCity"] + ', ' + player_dict["birthStateProvince"] + ', ' + player_dict["birthCountry"]
    else:
        player.birthplace = player_dict["birthCity"] + ', ' + player_dict["birthCountry"] 
    player.birthdate = player_dict["birthDate"]
    return player

def run():
    players = nhl.players_build(nhl.roster_url)
    roster = nhl.roster_build(players, nhl.player_url)
    for player in roster:
        print(json.dumps(player, indent=4))
    #    p = player_insert(player)
    #    p.save()
    