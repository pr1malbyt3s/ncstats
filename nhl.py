from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import json
import requests

# Set API Urls:
schedule_url = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=12&season=20202021"
roster_url = "https://statsapi.web.nhl.com/api/v1/teams/12?expand=team.roster"
player_url = "http://statsapi.web.nhl.com/api/v1/people/"

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
def schedule_build(url: str) -> list:
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
        away = str(x["games"][0]["teams"]["home"]["team"]["name"])
        home = str(x["games"][0]["teams"]["away"]["team"]["name"])
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

def player_list_build(url: str) -> list:
    player_list = []
    response = requests.get(url).json()
    for x in response["teams"][0]["roster"]["roster"]:
        player_id = str(x["person"]["id"])
        player_list.append(player_id)
    return player_list

def roster_build(player_list: list) -> list:
    roster = []
    for id in player_list:
        url = player_url + str(id)
        response = requests.get(url).json()
        for x in response["people"]:
            player_id = str(x["id"])
            name = x["fullName"]
            if "primaryNumber" in x:
                jersey = str(x["primaryNumber"])
            else:
                jersey = "N/A"
            age = str(x["currentAge"])
            height = str(x["height"])
            weight = str(x["weight"])
            group = x["primaryPosition"]["type"]
            position = x["primaryPosition"]["code"]
            if "birthStateProvince" in x:
                birthplace = x["birthCity"] + ', ' + x["birthStateProvince"] + ', ' + x["birthCountry"]
            else:
                birthplace = x["birthCity"] + ', ' + x["birthCountry"]
            birthdate = str(x["birthDate"])
            player = player_id + ' ' + name + ' ' + jersey + ' ' + age + ' ' + height + ' ' + weight + ' ' + group + ' ' + position + ' ' + birthplace + ' ' + birthdate
            roster.append(player)
    return roster


def main():
    # Generate the schedule:
    #for game in schedule_build(schedule_url):
    #    print(game)
    # Generate the roster:
    for player in roster_build(player_list_build(roster_url)):
        print(player)
    

if __name__ == "__main__":
    main()
