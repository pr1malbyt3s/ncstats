from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import json
import requests

# Set API Urls:
schedule_url = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=12&season=SEASON"
roster_url = "https://statsapi.web.nhl.com/api/v1/teams/12?expand=team.roster"
player_url = "https://statsapi.web.nhl.com/api/v1/people/PLAYER_ID"
player_overall_stats_url = "https://statsapi.web.nhl.com/api/v1/people/PLAYER_ID/stats?stats=statsSingleSeason&season=SEASON"
game_stats_url = "https://statsapi.web.nhl.com/api/v1/game/GAME_ID/boxscore"
game_score_url = "https://statsapi.web.nhl.com/api/v1/game/GAME_ID/linescore"

# Locations dictionary used to specify game location based on home/away and/or opponent:
locations = {
        "Carolina Hurricanes" : "Raleigh, NC",
        "Chicago Blackhawks" : "Chicago, IL",
        "Columbus Blue Jackets" : "Columbus, OH",
        "Dallas Stars" : "Dallas, TX",
        "Detroit Red Wings" : "Detroit, MI",
        "Florida Panthers" : "Sunrise, FL",
        "Nashville Predators" : "Nashville, TN",
        "Tampa Bay Lightning" : "Tampa, FL"
}

# Function used to build the game schedule. It accepts the API URL as the parameter and returns a dictionary of games:
def schedule_build(schedule_url:str, score_url:str, season:int) -> dict:
    # Initialize the schedule dictionary:
    schedule = {}
    url1 = schedule_url.replace("SEASON", str(season))
    # Get the API response as JSON:
    response1 = requests.get(url1).json()
    # Iterate through each game:
    for x in response1["dates"]:
        # Initialize the individual game dictionary:
        game = {}
        # Parse the game ID:
        game["gameId"] = x["games"][0]["gamePk"]
        # Parse the game season:
        game["season"] = x["games"][0]["season"]
        # Parse the game date:
        game["date"] = x["date"]
        # Parse the away and home teams:
        away = x["games"][0]["teams"]["away"]["team"]["name"]
        home = x["games"][0]["teams"]["home"]["team"]["name"]
        # Set the opponent based on the away and home teams:
        if  (away == "Carolina Hurricanes"):
            game["opponent"] = home
        else:
            game["opponent"] = away
        # Set the game location to the home team's city using the locations dictionary:
        game["location"] = locations[home]
        # Parse the gameDate datetime object, convert it to Eastern time, and return the HH:MM format:
        game["time"] = parse(x["games"][0]["gameDate"]).astimezone(timezone("US/Eastern")).strftime("%H:%M")
        # Parse the game state and mark it True for played and false for not played:
        status = x["games"][0]["status"]["detailedState"]
        if (status == "Final"):
            game["played"] = True
            url2 = score_url.replace("GAME_ID", str(game["gameId"]))
            response2 = requests.get(url2).json()
            if (away == "Carolina Hurricanes"):
                game["carScore"] = response2["teams"]["away"]["goals"]
                game["oppScore"] = response2["teams"]["home"]["goals"]
            else:
                game["carScore"] = response2["teams"]["home"]["goals"]
                game["oppScore"] = response2["teams"]["away"]["goals"]
            game["period"] = response2["currentPeriodOrdinal"]
        else:
            game["played"] = False
        # Add the game to the schedule dictionary:
        schedule[game["gameId"]] = game
    # Return the final schedule:
    return schedule

# Function used to build the list of players by ID. This is used for subsuqent functions. It accepts the API URL as the parameter and returns a dictionary of players:
def players_build(url:str) -> dict:
    # Initialize the individual player dictionary:
    players = {}
    # Get the API response as JSON:
    response = requests.get(url).json()
    # Iterate through each person on the roster:
    for x in response["teams"][0]["roster"]["roster"]:
        player = {}
        # Parse the player's ID:
        player["playerId"] = x["person"]["id"]
        # Parse the player's name:
        player["name"] = x["person"]["fullName"]
        # Add the player to the player dicitionary:
        players[player["playerId"]] = player
    # Return the dictionary of players:
    return players

# Function used to build the team roster. It accepts the players dictionary and the API URL as parameters and returns the roster as a dictionary of players:
def roster_build(players:dict, url:str) -> dict:
    # Initialize the roster dictionary:
    roster = {}
    # Iterate through each player ID in the player list:
    for key in players:
        # Initialize the individual player dictionary:
        player = {}
        # Update the URL to retrieve player info:
        url2 = url.replace("PLAYER_ID", str(key))
        # Get the API response as JSON. This uses the individual player URL by their ID:
        response = requests.get(url2).json()
        # Iterate through the player attributes:
        for key, val in response["people"][0].items():
            # Add each attribute to the player dictionary:
            player[key] = val
            # Add the player to the roster dictionary:
        roster[player["id"]] = player
        # Add Taxi Squad players manually until NHL fixes their roster API:
    roster[8474581] = {
        "id" : 8474581,
        "fullName" : "Jake Gardiner",
        "firstName" : "Jake",
        "lastName" : "Gardiner",
        "primaryNumber" : "51",
        "birthDate" : "1990-07-04",
        "currentAge" : 30,
        "birthCity" : "Minnetonka",
        "birthStateProvince" : "MN",
        "birthCountry" : "USA",
        "height" : "6' 2\"",
        "weight" : 203,
        "primaryPosition" : {
            "code" : "D",
            "name" : "Defenseman",
            "type" : "Defenseman",
            "abbreviation" : "D"
        }
    } 
    roster[8479987] = {
        "id" : 8479987,
        "fullName" : "Morgan Geekie",
        "firstName" : "Morgan",
        "lastName" : "Geekie",
        "primaryNumber" : "67",
        "birthDate" : "1998-07-20",
        "currentAge" : 22,
        "birthCity" : "Strathclair",
        "birthStateProvince" : "MB",
        "birthCountry" : "CAN",
        "height" : "6' 3\"",
        "weight" : 192,
        "primaryPosition" : {
            "code" : "C",
            "name" : "Center",
            "type" : "Forward",
            "abbreviation" : "C"
        }
    }
    roster[8478904] = {
        "id" : 8478904,
        "fullName" : "Steven Lorentz",
        "firstName" : "Steven",
        "lastName" : "Lorentz",
        "primaryNumber" : "78",
        "birthDate" : "1996-04-13",
        "currentAge" : 24,
        "birthCity" : "Kitchener",
        "birthStateProvince" : "ON",
        "birthCountry" : "CAN",
        "height" : "6' 4\"",
        "weight" : 206,
        "primaryPosition" : {
            "code" : "C",
            "name" : "Center",
            "type" : "Forward",
            "abbreviation" : "C"
        }
    }
    roster[8476323] = {
        "id" : 8476323,
        "fullName" : "Max McCormick",
        "firstName" : "Max",
        "lastName" : "McCormick",
        "primaryNumber" : "28",
        "birthDate" : "1992-05-01",
        "currentAge" : 28,
        "birthCity" : "De Pere",
        "birthStateProvince" : "WI",
        "birthCountry" : "USA",
        "height" : "5' 11\"",
        "weight" : 188,
        "primaryPosition" : {
            "code" : "L",
            "name" : "Left Wing",
            "type" : "Forward",
            "abbreviation" : "LW"
        }
    }
    roster[8479402] = {
        "id" : 8479402,
        "fullName" : "Jake Bean",
        "firstName" : "Jake",
        "lastName" : "Bean",
        "primaryNumber" : "24",
        "birthDate" : "1998-06-09",
        "currentAge" : 22,
        "birthCity" : "Calgary",
        "birthStateProvince" : "AB",
        "birthCountry" : "CAN",
        "height" : "6' 1\"",
        "weight" : 186,
        "primaryPosition" : {
            "code" : "D",
            "name" : "Defenseman",
            "type" : "Defenseman",
            "abbreviation" : "D"
        }
    }
    roster[8477968] = {
        "id" : 8477968,
        "fullName" : "Alex Nedeljkovic",
        "firstName" : "Alex",
        "lastName" : "Nedeljkovic",
        "primaryNumber" : "39",
        "birthDate" : "1996-01-07",
        "currentAge" : 25,
        "birthCity" : "Parma",
        "birthStateProvince" : "OH",
        "birthCountry" : "USA",
        "height" : "6' 0\"",
        "weight" : 189,
        "primaryPosition" : {
            "code" : "G",
            "name" : "Goalie",
            "type" : "Goalie",
            "abbreviation" : "G"
        }
    }
    roster[8480776] = {
        "id" : 8480776,
        "fullName" : "Sheldon Rempal",
        "firstName" : "Sheldon",
        "lastName" : "Rempal",
        "primaryNumber" : "41",
        "birthDate" : "1995-08-07",
        "currentAge" : 25,
        "birthCity" : "Calgary",
        "birthStateProvince" : "AB",
        "birthCountry" : "CAN",
        "height" : "5' 10\"",
        "weight" : 165,
        "primaryPosition" : {
            "code" : "R",
            "name" : "Right Wing",
            "type" : "Forward",
            "abbreviation" : "RW"
        }
    }
    roster[8475213] = {
        "id" : 8475213,
        "fullName" : "Drew Shore",
        "firstName" : "Drew",
        "lastName" : "Shore",
        "primaryNumber" : "29",
        "birthDate" : "1991-01-29",
        "currentAge" : 30,
        "birthCity" : "Denver",
        "birthStateProvince" : "CO",
        "birthCountry" : "USA",
        "height" : "6' 2\"",
        "weight" : 209,
        "primaryPosition" : {
            "code" : "C",
            "name" : "Center",
            "type" : "Forward",
            "abbreviation" : "C"
        }
    }
    roster[8476288] = {
        "id" : 8476288,
        "fullName" : "Ryan Dzingel",
        "firstName" : "Ryan",
        "lastName" : "Dzingel",
        "primaryNumber" : "10",
        "birthDate" : "1992-03-09",
        "currentAge" : 28,
        "birthCity" : "Wheaton",
        "birthStateProvince" : "IL",
        "birthCountry" : "USA",
        "height" : "6' 0\"",
        "weight" : 190,
        "primaryPosition" : {
            "code" : "L",
            "name" : "Left Wing",
            "type" : "Forward",
            "abbreviation" : "LW"
        }
    }
    roster[8477046] = {
        "id" : 8477046,
        "fullName" : "Joakim Ryan",
        "firstName" : "Joakim",
        "lastName" : "Ryan",
        "primaryNumber" : "33",
        "birthDate" : "1993-06-17",
        "currentAge" : 27,
        "birthCity" : "Rumson",
        "birthStateProvince" : "NJ",
        "birthCountry" : "USA",
        "height" : "5' 11\"",
        "weight" : 185,
        "primaryPosition" : {
            "code" : "D",
            "name" : "Defenseman",
            "type" : "Defenseman",
            "abbreviation" : "D"
        }
    }
    # Return the final roster dictionary:
    return roster

# Function used to build overall stats for players. It accepts a list of stats from the API response, the player's ID as an integer, and the player's name as string to produce a stats dictionary:
def overall_stats_individual_build(stats:list, player_id:int, name:str) -> dict:
    # Initialize the dictionary, storing the player's ID and name:
    player = {"playerId":player_id, "name":name}
    # Check if the response contains the player's stats:
    if(stats):
        # If so, add the season to the dictionary:
        player["season"] = stats[0]["season"]
        # Iterate through all remaining stats by key and value:
        for key, val in stats[0]["stat"].items():
            # Add each key/value pair to the dictionary:
            player[key] = val
    # Return the player dictionary:
    return player    

# Function used to get overall stats. It accepts the roster dictionary and the API url as parameters and returns a dictionary of overall stats for every player:
def overall_stats_total_build(roster:dict, url:str, season:int) -> dict:
    # Initialize the goalie stats dictionary:
    goalie_stats = {}
    # Initialize the skater stats dictionary:
    skater_stats = {}
    # Iterate through each player on the roster:
    for key in roster:
        # Adjust the API url for player_id:
        url2 = url.replace("PLAYER_ID", str(key)).replace("SEASON", str(season))
        # Get the API response as JSON. This uses the individual player URL by their ID:
        response = requests.get(url2).json()
        # Check if the player is a goalie:
        if (roster[key]["primaryPosition"]["name"] == "Goalie"):
            # If so, add to the players dictionary:
            goalie_stats[key] = overall_stats_individual_build(response["stats"][0]["splits"], key, roster[key]["fullName"])
        # Otherwise the player is a skater:
        else:
            # Add to the skaters dictionary:
            skater_stats[key] = overall_stats_individual_build(response["stats"][0]["splits"], key, roster[key]["fullName"])
    # Create the overall_stats dictionary from skater and goalie stats:
    overall_stats = {"skater_stats":skater_stats, "goalie_stats":goalie_stats}    
    # Return the overall stats dictionary:
    return overall_stats

# Function used to build individual player stats for a game. It accepts the player's stats dictionary parsed from the API url and build's the player's stats based on position, returning a dictionary of stats for the player:
def game_stats_individual_build(player:dict) -> dict:
    # Initialize the player_stats dictionary with the player's id and name:
    player_stats = {"playerId":player["person"]["id"], "name":player["person"]["fullName"]}
    # Check if the player's stats are goalieStats:
    if ("goalieStats" in player["stats"]):
        # If so, iterate through each key/value in goalieStats:
       for key, val in player["stats"]["goalieStats"].items():
            # And build the player's stats:
            player_stats[key] = val
    # Otherwise, check if the player's stats are skaterStats:
    elif ("skaterStats" in player["stats"]):
        # If so, iterate through each key/value in skaterStats:
        for key, val in player["stats"]["skaterStats"].items():
            # And build the player's stats:
            player_stats[key] = val 
    # If the player doesn't have stats (likely due to scratch):
    else:
        # Return an empty object
        return
    # Return the player_stats dictionary:
    return player_stats

# Function used to get individual game stats. It accepts the game_id and the API url and returns a dictionary of stats for the provided game_id:
def game_stats_total_build(game_id:int, url:str) -> dict:
    # Initialize the game_stats dictionary with the game_id:
    game_stats = {}
    # Update the url based on the game_id:
    url2 = url.replace("GAME_ID", str(game_id))
    # Get the API response as JSON:
    response = requests.get(url2).json()
    # Check if Canes are home or away:
    if (response["teams"]["away"]["team"]["name"] == "Carolina Hurricanes"):
        # If away, get away team stats:
        stats = response["teams"]["away"]["players"]
    else:
        # If home, get home team stats:
        stats = response["teams"]["home"]["players"]
    # Iterate through each key/value pair in the response:
    for _,player in stats.items():
        # Convert the player_id to a string:
        player_id = str(player["person"]["id"])
        # Use the game_stats_individual_build function to build game stats for each player id:
        game_stats[player_id] = game_stats_individual_build(player)
    # Only keep players with stats available, accounting for scratched players:
    game_stats = {key:val for key, val in game_stats.items() if val}
    # Return the game stats dictionary:
    return game_stats

def run():
    # Generate the schedule:
    schedule = schedule_build(schedule_url, game_score_url, 20202021)
    print(json.dumps(schedule, indent=4))
    # Generate the player list:
    #players = players_build(roster_url)
    #print(json.dumps(players, indent=4))
    # Generate the roster:
    #roster = roster_build(players, player_url)
    #print(json.dumps(roster, indent=4))
    # Generate the overall basic skater stats:
    #overall_stats = overall_stats_total_build(roster, player_overall_stats_url, 20202021)
    #print(json.dumps(overall_stats, indent=4))
    # Generate game stats for a sample game:
    #game_stats = game_stats_total_build(2020020025, game_stats_url)
    #print(json.dumps(game_stats, indent=4))
