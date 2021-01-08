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
def goalie_stats_build(stats:list, player_id:int, name:str) -> dict:
    goalie = {"playerId":player_id, "name":name}
    if(stats):
        for x in stats:
            goalie["season"] = x["season"]
            goalie["games"] = x["stat"]["games"]
            goalie["wins"] = x["stat"]["wins"]
            goalie["losses"] = x["stat"]["losses"]
            goalie["ties"] = x["stat"]["ties"]
            goalie["started"] = x["stat"]["gamesStarted"]
            goalie["saves"] = x["stat"]["saves"]
            goalie["shotsa"] = x["stat"]["shotsAgainst"]
            goalie["goalsa"] = x["stat"]["goalsAgainst"]
            goalie["toipg"] = x["stat"]["timeOnIcePerGame"]
            goalie["svpct"] = x["stat"]["savePercentage"]
            goalie["gaa"] = x["stat"]["goalAgainstAverage"]
            goalie["ot"] = x["stat"]["ot"]
            goalie["shutouts"] = x["stat"]["shutouts"]
            goalie["essaves"] = x["stat"]["evenSaves"]
            goalie["ppsaves"] = x["stat"]["powerPlaySaves"]
            goalie["shsaves"] = x["stat"]["shortHandedSaves"]
            goalie["esshots"] = x["stat"]["evenShots"]
            goalie["ppshots"] = x["stat"]["powerPlayShots"]
            goalie["shshots"] = x["stat"]["shortHandedShots"]
            goalie["essvpct"] = x["stat"]["evenStrengthSavePercentage"]
            goalie["ppsvpct"] = x["stat"]["powerPlaySavePercentage"]
            goalie["shsvpct"] = x["stat"]["shortHandedSavePercentage"]
    return goalie

# Function used to build stats for skaters. It accepts a list of stats from the API response, the player's ID as an integer, and the player's name as string to produce a dicitonary of the skater's stats:
def skater_stats_build(stats:list, player_id:int, name:str) -> dict:
    skater = {"playerId":player_id, "name":name}
    if(stats):
        for x in stats:
            skater["season"] = x["season"]
            skater["games"] = x["stat"]["games"]
            skater["goals"] = x["stat"]["goals"]
            skater["assists"] = x["stat"]["assists"]
            skater["points"] = x["stat"]["points"]
            skater["pim"] = x["stat"]["pim"]
            skater["plusMinus"] = x["stat"]["plusMinus"]
            skater["toipg"] = x["stat"]["timeOnIcePerGame"]
            skater["ppg"] = x["stat"]["powerPlayGoals"]
            skater["ppa"] = x["stat"]["powerPlayPoints"] - skater["ppg"]
            skater["shg"] = x["stat"]["shortHandedGoals"]
            skater["sha"] = x["stat"]["shortHandedPoints"] - skater["shg"]        
    return skater    

# Function used to get overall stats. It acc 
def overall_stats_build(roster:dict, url:str) -> dict:
    goalie_stats = {}
    skater_stats = {}
    for key in roster:
        url2 = url.replace("PLAYER_ID", str(key))
        response = requests.get(url2).json()
        if (roster[key]["group"] == "Goalie"):
            goalie_stats[key] = goalie_stats_build(response["stats"][0]["splits"], key, roster[key]["name"])
        else:
            skater_stats[key] = skater_stats_build(response["stats"][0]["splits"], key, roster[key]["name"])
    overall_stats = {"skater_stats":skater_stats, "goalie_stats":goalie_stats}    
    return overall_stats

def main():
    # Generate the schedule:
    #schedule = schedule_build(schedule_url)
    #print(json.dumps(schedule, indent=4))
    # Generate the player list:
    players = players_build(roster_url)
    #print(json.dumps(players, indent=4))
    # Generate the roster:
    roster = roster_build(players, player_url)
    print(json.dumps(roster, indent=4))
    # Generate the overall basic skater stats:
    overall_stats = overall_stats_build(roster, player_overall_stats_url)
    print(json.dumps(overall_stats, indent=4))
    
if __name__ == "__main__":
    main()
