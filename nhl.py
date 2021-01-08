from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import json
import requests

# Set API Urls:
schedule_url = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=12&season=20202021"
roster_url = "https://statsapi.web.nhl.com/api/v1/teams/12?expand=team.roster"
player_url = "http://statsapi.web.nhl.com/api/v1/people/"
player_overall_stats_url_1 = "http://statsapi.web.nhl.com/api/v1/people/"
player_overall_stats_url_2 = "/stats?stats=statsSingleSeason&season=20192020"


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

# Function used to build the game schedule. It accepts the API URL as the parameter and returns a list of games:
def schedule_build(url:str) -> list:
    # Initialize the schedule list:
    schedule = []
    # Get the API response as JSON:
    response = requests.get(url).json()
    # Iterate through each game:
    for x in response["dates"]:
        # Parse the game ID:
        game_id = str(x["games"][0]["gamePk"])
        # Parse the game date:
        date = str(x["date"])
        # Parse the away and home teams:
        away = x["games"][0]["teams"]["home"]["team"]["name"]
        home = x["games"][0]["teams"]["away"]["team"]["name"]
        # Set the opponent based on the away and home teams:
        if  (away == "Carolina Hurricanes"):
            opponent = home
        else:
            opponent = away
        # Set the game location to the home team's city using the locations dictionary:
        location = locations[home]
        # Parse the gameDate datetime object, convert it to Eastern time, and return the HH:MM format:
        time = str(parse(x["games"][0]["gameDate"]).astimezone(timezone("US/Eastern")).strftime("%H:%M"))
        # Generate the game string for database storage:
        game = game_id + ' ' + date + ' ' + opponent + ' ' + location + ' ' + time
        # Append the game string to the schedule list:
        schedule.append(game)
    # Return the final schedule:
    return schedule

# Function used to build the list of player IDs. This list is used for subsuqent functions. It accepts the API URL as the parameter and returns a list of player IDs:
def player_list_build(url:str) -> list:
    # Initialize the player list:
    player_list = []
    # Get the API response as JSON:
    response = requests.get(url).json()
    # Iterate through each person on the roster:
    for x in response["teams"][0]["roster"]["roster"]:
        # Parse the player's ID:
        player_id = str(x["person"]["id"])
        # Append the ID to the player list:
        player_list.append(player_id)
    # Return the list of player IDs:
    return player_list

# Function used to build the team roster. It accepts the list of player IDs and the API URL as parameters and returns the roster as a list of players:
def roster_build(player_list:list, url:str) -> list:
    # Initialize the roster list:
    roster = []
    # Iterate through each player ID in the player list:
    for id in player_list:
        # Get the API response as JSON. This uses the individual player URL by their ID:
        response = requests.get(url + str(id)).json()
        # Iterate through the player attributes:
        for x in response["people"]:
            # Parse the player ID:
            player_id = str(x["id"])
            # Parse the player name:
            name = x["fullName"]
            # Check if player has a jersey number:
            if "primaryNumber" in x:
                # If so, parse the jersey number:
                jersey = str(x["primaryNumber"])
            else:
                # Otherwise, assign "N/A":
                jersey = "N/A"
            # Parse the player age:
            age = str(x["currentAge"])
            # Parse the player height:
            height = str(x["height"])
            # Parse the player weight:
            weight = str(x["weight"])
            # Parse the player position group:
            group = x["primaryPosition"]["type"]
            # Parse the player position:
            position = x["primaryPosition"]["code"]
            # Check if player has a birth province or state:
            if "birthStateProvince" in x:
                # If so, parse birthplace to include city, state/province, and country:
                birthplace = x["birthCity"] + ', ' + x["birthStateProvince"] + ', ' + x["birthCountry"]
            else:
                # Otherwise, parse birthdate to include city and country:
                birthplace = x["birthCity"] + ', ' + x["birthCountry"]
            # Parse the player birthdate:
            birthdate = str(x["birthDate"])
            # Generate the player string for database storage:
            player = player_id + ' ' + name + ' ' + jersey + ' ' + age + ' ' + height + ' ' + weight + ' ' + group + ' ' + position + ' ' + birthplace + ' ' + birthdate
            # Append the player to the roster list:
            roster.append(player)
    # Return the final roster list:
    return roster

# Function used to get overall skater stats. 
def overall_skater_stats_basic_build(player_list:list, url1:str, url2:str) -> list:
    overall_basic_skater_stats = []
    for id in player_list:
        url = url1 + str(id) + url2
        response = requests.get(url).json()
        for x in response["stats"][0]["splits"]:
            if "ot" in x["stat"]:
                overall_basic_skater_stats.append("Goalie")
            else:
                season = str(x["season"])
                games = str(x["stat"]["games"])
                goals = str(x["stat"]["goals"])
                assists = str(x["stat"]["assists"])
                points = str(x["stat"]["points"])
                pim = str(x["stat"]["pim"])
                plus_minus = str(x["stat"]["plusMinus"])
                toipg = str(x["stat"]["timeOnIcePerGame"])
                ppg = str(x["stat"]["powerPlayGoals"])
                ppa = str(x["stat"]["powerPlayPoints"] - int(ppg))
                shg = str(x["stat"]["shortHandedGoals"])
                sha = str(x["stat"]["shortHandedPoints"] - int(shg))
                skater_stats = season + ' ' + games + ' ' + goals + ' ' + assists + ' ' + points + ' ' + pim + ' ' + plus_minus + ' ' + toipg + ' ' + ppg + ' ' + ppa + ' ' + shg + ' ' + sha    
                overall_basic_skater_stats.append(skater_stats)
    return overall_basic_skater_stats

def main():
    # Generate the schedule:
    schedule = schedule_build(schedule_url)
    # Generate the player list:
    player_list = player_list_build(roster_url)
    # Generate the roster:
    roster = roster_build(player_list, player_url)
    # Generate the overall basic skater stats:
    overall_skater_stats_basic = overall_skater_stats_basic_build(player_list, player_overall_stats_url_1, player_overall_stats_url_2)
    print(overall_skater_stats_basic)
    
if __name__ == "__main__":
    main()
