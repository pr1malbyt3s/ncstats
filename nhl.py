from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import json
import requests

# Set API Urls:
schedule_url = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=12&season=20202021"
roster_url = "https://statsapi.web.nhl.com/api/v1/teams/12?expand=team.roster"
player_url = "https://statsapi.web.nhl.com/api/v1/people/PLAYER_ID"
player_overall_stats_url = "https://statsapi.web.nhl.com/api/v1/people/PLAYER_ID/stats?stats=statsSingleSeason&season=20192020"
game_stats_url = "https://statsapi.web.nhl.com/api/v1/game/GAME_ID/boxscore"

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
def schedule_build(url:str) -> dict:
    # Initialize the schedule dictionary:
    schedule = {}
    # Get the API response as JSON:
    response = requests.get(url).json()
    # Iterate through each game:
    for x in response["dates"]:
        # Initialize the individual game dictionary:
        game = {}
        # Parse the game ID:
        game["gameId"] = x["games"][0]["gamePk"]
        # Parse the game date:
        game["date"] = x["date"]
        # Parse the away and home teams:
        away = x["games"][0]["teams"]["home"]["team"]["name"]
        home = x["games"][0]["teams"]["away"]["team"]["name"]
        # Set the opponent based on the away and home teams:
        if  (away == "Carolina Hurricanes"):
            game["opponent"] = home
        else:
            game["opponent"] = away
        # Set the game location to the home team's city using the locations dictionary:
        game["location"] = locations[home]
        # Parse the gameDate datetime object, convert it to Eastern time, and return the HH:MM format:
        game["time"] = parse(x["games"][0]["gameDate"]).astimezone(timezone("US/Eastern")).strftime("%H:%M")
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
def roster_build(players:dict, url:str) -> list:
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
        for x in response["people"]:
            # Parse the player ID:
            player["playerId"] = x["id"]
            # Parse the player name:
            player["name"] = x["fullName"]
            # Check if player has a jersey number:
            if "primaryNumber" in x:
                # If so, parse the jersey number:
                player["jersey"] = x["primaryNumber"]
            else:
                # Otherwise, assign "N/A":
                player["jersey"] = "N/A"
            # Parse the player age:
            player["age"] = x["currentAge"]
            # Parse the player height:
            player["height"] = x["height"]
            # Parse the player weight:
            player["weight"] = x["weight"]
            # Parse the player position group:
            player["group"] = x["primaryPosition"]["type"]
            # Parse the player position:
            player["position"] = x["primaryPosition"]["code"]
            # Check if player has a birth province or state:
            if "birthStateProvince" in x:
                # If so, parse birthplace to include city, state/province, and country:
                player["birthplace"] = x["birthCity"] + ', ' + x["birthStateProvince"] + ', ' + x["birthCountry"]
            else:
                # Otherwise, parse birthdate to include city and country:
                player["birthplace"] = x["birthCity"] + ', ' + x["birthCountry"]
            # Parse the player birthdate:
            player["birthdate"] = x["birthDate"]
            # Add the player to the roster dictionary:
            roster[player["playerId"]] = player
    # Return the final roster dictionary:
    return roster

# Function used to build stats for goalies. It accepts a list of stats from the API response, the player's ID as an integer, and the player's name as string to produce a dicitonary of the goalie's stats:
def goalie_stats_overall_build(stats:list, player_id:int, name:str) -> dict:
    # Initialize the dictionary, storing the player's ID and name:
    goalie = {"playerId":player_id, "name":name}
    # Check if response contains the player's stats:
    if(stats):
        # If so, iterate through the response list:
        for x in stats:
            # Parse the season:
            goalie["season"] = x["season"]
            # Parse games played:
            goalie["games"] = x["stat"]["games"]
            # Parse games won:
            goalie["wins"] = x["stat"]["wins"]
            # Parse games lost:
            goalie["losses"] = x["stat"]["losses"]
            # Parse games tied:
            goalie["ties"] = x["stat"]["ties"]
            # Parse games started:
            goalie["started"] = x["stat"]["gamesStarted"]
            # Parse player saves:
            goalie["saves"] = x["stat"]["saves"]
            # Parse player shots against:
            goalie["shotsa"] = x["stat"]["shotsAgainst"]
            # Parse player goals against:
            goalie["goalsa"] = x["stat"]["goalsAgainst"]
            # Parse player time on ice per game:
            goalie["toipg"] = x["stat"]["timeOnIcePerGame"]
            # Parse player save percentage:
            goalie["svpct"] = x["stat"]["savePercentage"]
            # Parse player goals against average:
            goalie["gaa"] = x["stat"]["goalAgainstAverage"]
            # Parse overtime games:
            goalie["ot"] = x["stat"]["ot"]
            # Parse player shutouts:
            goalie["shutouts"] = x["stat"]["shutouts"]
            # Parse even strength saves:
            goalie["essaves"] = x["stat"]["evenSaves"]
            # Parse powerplay saves:
            goalie["ppsaves"] = x["stat"]["powerPlaySaves"]
            # Parse shorthanded saves:
            goalie["shsaves"] = x["stat"]["shortHandedSaves"]
            # Parse even strength shots against:
            goalie["esshots"] = x["stat"]["evenShots"]
            # Parse powerplay shots against:
            goalie["ppshots"] = x["stat"]["powerPlayShots"]
            # Parse shorthanded shots agains:
            goalie["shshots"] = x["stat"]["shortHandedShots"]
            # Parse even strength save percentage:
            goalie["essvpct"] = x["stat"]["evenStrengthSavePercentage"]
            # Parse powerplay save percentage:
            goalie["ppsvpct"] = x["stat"]["powerPlaySavePercentage"]
            # Parse shorthanded save percentage:
            goalie["shsvpct"] = x["stat"]["shortHandedSavePercentage"]
    return goalie

# Function used to build stats for skaters. It accepts a list of stats from the API response, the player's ID as an integer, and the player's name as string to produce a dicitonary of the skater's stats:
def skater_stats_overall_build(stats:list, player_id:int, name:str) -> dict:
    # Initialize the dictionary, storing the player's ID and name:
    skater = {"playerId":player_id, "name":name}
    # Check if the response contains the player's stats:
    if(stats):
        # If so, iterate through the response list:
        for x in stats:
            # Parse the season:
            skater["season"] = x["season"]
            # Parse games played:
            skater["games"] = x["stat"]["games"]
            # Parse player goals:
            skater["goals"] = x["stat"]["goals"]
            # Parse player assists:
            skater["assists"] = x["stat"]["assists"]
            # Parse player points:
            skater["points"] = x["stat"]["points"]
            # Parse player penalty minutes:
            skater["pim"] = x["stat"]["pim"]
            # Parse player plus/minus rating:
            skater["plusMinus"] = x["stat"]["plusMinus"]
            # Parse player time on ice per game:
            skater["toipg"] = x["stat"]["timeOnIcePerGame"]
            # Parse player powerplay goals:
            skater["ppg"] = x["stat"]["powerPlayGoals"]
            # Parse player powerplay assists by subtracting powerplay goals from powerplay points:
            skater["ppa"] = x["stat"]["powerPlayPoints"] - skater["ppg"]
            # Parse player shorthanded goals:
            skater["shg"] = x["stat"]["shortHandedGoals"]
            # Parse player shorthanded assists by subtracting shorthanded goals from shorthanded points:
            skater["sha"] = x["stat"]["shortHandedPoints"] - skater["shg"]
            # Parse player even strength time on ice per game:
            skater["etoipg"] = x["stat"]["evenTimeOnIcePerGame"]
            # Parse player shorthanded time on ice per game:
            skater["shtoipg"] = x["stat"]["shortHandedTimeOnIcePerGame"]
            # Parse player powerplay time on ice per game:
            skater["pptoipg"] = x["stat"]["powerPlayTimeOnIcePerGame"]
            # Parse player shots:
            skater["shots"] = x["stat"]["shots"]
            # Parse player shot percentage:
            skater["shotpct"] = x["stat"]["shotPct"]
            # Parse player faceoff percentage:
            skater["fopct"] = x["stat"]["faceOffPct"]
            # Parse player blocks:
            skater["blocks"] = x["stat"]["blocked"]
            # Parse player hits:
            skater["hits"] = x["stat"]["hits"]
            # Parse player shifts:
            skater["shifts"] = x["stat"]["shifts"]
            # Parse player game winning goals:
            skater["gwg"] = x["stat"]["gameWinningGoals"]
    return skater    

# Function used to get overall stats. It accepts the roster dictionary and the API url as parameters and returns a dictionary of overall stats for every player:
def overall_stats_build(roster:dict, url:str) -> dict:
    # Initialize the goalie stats dictionary:
    goalie_stats = {}
    # Initialize the skater stats dictionary:
    skater_stats = {}
    # Iterate through each player on the roster:
    for key in roster:
        # Adjust the API url for player_id:
        url2 = url.replace("PLAYER_ID", str(key))
        # Get the API response as JSON. This uses the individual player URL by their ID:
        response = requests.get(url2).json()
        # Check if the player is a goalie:
        if (roster[key]["group"] == "Goalie"):
            # If so, use the goalie_stats_build function:
            goalie_stats[key] = goalie_stats_build(response["stats"][0]["splits"], key, roster[key]["name"])
        # Otherwise the player is a skater:
        else:
            # Use the skater_stats_build function:
            skater_stats[key] = skater_stats_build(response["stats"][0]["splits"], key, roster[key]["name"])
    # Create the overall_stats dictionary from skater and goalie stats:
    overall_stats = {"skater_stats":skater_stats, "goalie_stats":goalie_stats}    
    # Return the overall stats dictionary:
    return overall_stats

def game_stats_individual_build(player:dict) -> dict:
    player_stats = {"playerId":player["person"]["id"], "name":player["person"]["fullName"]}
    if ("goalieStats" in player["stats"]):
       for key, val in player["stats"]["goalieStats"].items():
            player_stats[key] = val
    elif ("skaterStats" in player["stats"]):
        for key, val in player["stats"]["skaterStats"].items():
            player_stats[key] = val 
    else:
        return
    return player_stats

def game_stats_total_build(game_id:int, url:str) -> dict:
    game_stats = {"gameId": game_id}
    url2 = url.replace("GAME_ID", str(game_id))
    response = requests.get(url2).json()
    # Check if Canes are home or away:
    if (response["teams"]["away"]["team"]["name"] == "Carolina Hurricanes"):
        stats = response["teams"]["away"]["players"]
    else:
        stats = response["teams"]["home"]["players"]
    for _,player in stats.items():
        player_id = str(player["person"]["id"])
        game_stats[player_id] = game_stats_individual_build(player)
    game_stats = {key:val for key, val in game_stats.items() if val}
    return game_stats


def main():
    # Generate the schedule:
    #schedule = schedule_build(schedule_url)
    #print(json.dumps(schedule, indent=4))
    # Generate the player list:
    #players = players_build(roster_url)
    #print(json.dumps(players, indent=4))
    # Generate the roster:
    #roster = roster_build(players, player_url)
    #print(json.dumps(roster, indent=4))
    # Generate the overall basic skater stats:
    #overall_stats = overall_stats_build(roster, player_overall_stats_url)
    game_stats = game_stats_total_build(2019020569, game_stats_url)
    print(json.dumps(game_stats, indent=4))
    
if __name__ == "__main__":
    main()
