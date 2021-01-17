from . import nhl
from stormstats.models import *
import json

# Game construct function used to build Game objects. It accepts the game dictionary built by the schedule_build nhl function and parses needed values from the JSON, returning a Game object:
def game_construct(game_dict:dict) -> Game:
    # Initialize the Game object:
    game = Game()
    # Parse the game's id:
    game.game_id = game_dict["gameId"]
    # Parse the game's date:
    game.date = game_dict["date"]
    # Parse the game's opponent:
    game.opponent = game_dict["opponent"]
    # Parse the game's location:
    game.location = game_dict["location"]
    # Parse the game's time:
    game.time = game_dict["time"]
    # Return the game object:
    return game

# Player construct function used to build player objects. It accepts the player dictionary built by the roster_build nhl function and parses needed values from the JSON, returning a Player object:
def player_construct(player_dict:dict) -> Player:
    # Initialize the Player object:
    player = Player()
    # Parse the player's id:
    player.player_id = player_dict["id"]
    # Parse the player's name:
    player.name = player_dict["fullName"]
    # Parse the player's jersey number:
    player.jersey = player_dict["primaryNumber"]
    # Parse the player's age:
    player.age = player_dict["currentAge"]
    # Parse the player's height:
    player.height = player_dict["height"].replace('"', '')
    # Parse the player's weight:
    player.weight = player_dict["weight"]
    # Parse the player's position type:
    player.group = player_dict["primaryPosition"]["type"]
    # Parse the player's position:
    player.position = player_dict["primaryPosition"]["name"]
    # Parse the player's birth place:
    if ("birthStateProvince" in player_dict):
        # If it has a province/state include it:
        player.birthplace = player_dict["birthCity"] + ', ' + player_dict["birthStateProvince"] + ', ' + player_dict["birthCountry"]
    else:
        # If not, birthplace is city and country:
        player.birthplace = player_dict["birthCity"] + ', ' + player_dict["birthCountry"] 
    # Parse the player's birthday:
    player.birthdate = player_dict["birthDate"]
    # Return the player object:
    return player

# Games insert function used to build the schedule, iterate through the games, build each Game object, and insert it into the database:
def games_insert():
    # Build the schedule using the nhl.schedule_build function:
    schedule = nhl.schedule_build(nhl.schedule_url)
    # Iterate through the schedule dictionary by game:
    for _, val in schedule.items():
        # Construct the Game object from the game's attributes:
        g = game_construct(val)
        # Save the object to the database:
        g.save()

# Players insert function used to build the roster, iterate through the players, build each Player object, and insert it into the database:
def players_insert():
    # Get the list of players by name and id using the nhl.players_build function:
    players = nhl.players_build(nhl.roster_url)
    # Build the roster using the players list:
    roster = nhl.roster_build(players, nhl.player_url)
    # Iterate through the roster dictionary by player:
    for _, val in roster.items():
        # Construct the Player object from the player's attributes:
        p = player_construct(val)
        # Save the object to the database:
        p.save()

# Run function needed for the runscripts extension to execute:
def run():
    games_insert()