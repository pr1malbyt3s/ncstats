from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
import json
import requests

# Set API Urls:
schedule_url = "https://statsapi.web.nhl.com/api/v1/schedule?teamId=12&season=20202021"

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

def schedule_build(url: str) -> list:
    schedule = []
    response = requests.get(url).json()
    for x in response["dates"]:
        game_id = str(x["games"][0]["gamePk"])
        date = str(x["date"])
        away = str(x["games"][0]["teams"]["home"]["team"]["name"])
        home = str(x["games"][0]["teams"]["away"]["team"]["name"])
        if  (away == "Carolina Hurricanes"):
            opponent = home
        else:
            opponent = away
        location = locations[home]
        # YYYY-MM-DDTHH:MM:SSZ
        time = str(parse(x["games"][0]["gameDate"]).astimezone(timezone("US/Eastern")).strftime("%H:%M"))
        game = game_id + ' ' + date + ' ' + opponent + ' ' + location + ' ' + time
        schedule.append(game)
    return schedule

def main():
    schedule = schedule_build(schedule_url)
    for game in schedule:
        print(game)

if __name__ == "__main__":
    main()
