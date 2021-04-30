from . import nhl
from geopy.geocoders import Nominatim
from stormstats.models import *
import json

# Get the list of players by name and id using the nhl.players_build function:
players = nhl.players_build(nhl.roster_url)
# Build the roster using the players list:
roster = nhl.roster_build(players, nhl.player_url)

# Game construct function used to build Game objects. It accepts the game dictionary built by the schedule_build nhl function and parses needed values from the JSON, returning a Game object:
def game_construct(game_dict:dict) -> Game:
    def game_result(car_score:int, opp_score:int, p:str) -> str:
        s = str(car_score) + " - " + str(opp_score)
        r = ""
        if (car_score > opp_score):
            ss = "W {}".format(s)
        else:
            ss = "L {}".format(s)
        if (p == "OT" or p == "SO"):
            r = ss + " ({})".format(p)
        else:
            r = ss
        return r
    
    # Initialize the Game object:
    game, _ = Game.objects.update_or_create(game_id=game_dict["gameId"],
    defaults={
        # Parse the game's season:
        "season": game_dict.get("season", 20202021),
        # Parse the game's date:
        "date": game_dict.get("date", "01-01-00"),
        # Parse the game's opponent:
        "opponent": game_dict.get("opponent", "Chicago Blackhawks"),
        # Parse the game's location:
        "location": game_dict.get("location", "Raleigh, NC"),
        # Parse the game's time:
        "time": game_dict.get("time", "7:00"),
        # Parse the game's status:
        "played": game_dict.get("played", False),
        # Parse the game's result:
        "result": game_result(game_dict.get("carScore", 0), game_dict.get("oppScore", 0), game_dict.get("period", "N/A"))
    })
    # Return the game object:
    return game

# Player construct function used to build player objects. It accepts the player dictionary built by the roster_build nhl function and parses needed values from the JSON, returning a Player object:
def player_construct(player_dict:dict) -> Player:
    def height_in_inches(h:str) -> int:
        x = h.split("'")
        feet = int(x[0])
        inches = int(x[1])
        return feet*12 + inches

    def province_check(d:dict) -> str:
        if "birthStateProvince" in d:
            return d.get("birthCity", "CITY") + ', ' + d.get("birthStateProvince", "PROVINCE") + ', ' + d.get("birthCountry", "COUNTRY")
        return d.get("birthCity", "CITY") + ', ' + d.get("birthCountry", "COUNTRY")
    
    def geolocate(p:str) -> list:
        geolocator = Nominatim(user_agent="StormStats")
        x = p.split(', ')
        if (len(x) == 3):
            if (x[2] == 'USA'):
                try:
                    loc = geolocator.geocode(p)
                    return [loc.latitude, loc.longitude]
                except:
                    loc = geolocator.geocode(x[0] + ', ' + x[1])
                    return [loc.latitude, loc.longitude]
            else:
                try:
                    loc = geolocator.geocode(x[0] + ', ' + x[1])
                    return [loc.latitude, loc.longitude]
                except:
                    loc = geolocator.geocode(x[0])
                    return [loc.latitude, loc.longitude]
        else:
            try:
                loc = geolocator.geocode(p)
                return [loc.latitude, loc.longitude]
            except:
                loc = geolocator.geocode(x[0])
                return [loc.latitude, loc.longitude]
            
    # Initialize the Player object with player_id:
    player, _ = Player.objects.update_or_create(player_id=player_dict["id"],
    defaults={
        # Parse the player's name:
        "name": player_dict.get("fullName", "NAME"),
        # Parse the player's jersey number:
        "jersey": player_dict.get("primaryNumber", 00),
        # Parse the player's age:
        "age": player_dict.get("currentAge", 00),
        # Parse the player's height:
        "height_str": player_dict.get("height", "0' 0\"").replace('"', ''),
        # Convert height:
        "height": height_in_inches(player_dict.get("height", "0' 0\"").replace('"', '')),
        # Parse the player's weight:
        "weight": player_dict.get("weight", 0),
        # Parse the player's position type:
        "group": player_dict.get("primaryPosition", "type").get("type", "POS_TYPE"),
        # Parse the player's position:
        "position": player_dict.get("primaryPosition", "name").get("name", "POS_NAME"),
        # Parse the player's birth place. If it has a province/state include it. If not, birthplace is city and country:
        "birthplace": province_check(player_dict),
        # Parse the player's birthplace latitude:
        "bp_lat": geolocate(province_check(player_dict))[0],
        # Parse the player's birthplace longitude:
        "bp_long": geolocate(province_check(player_dict))[1],
        # Parse the player's birthday:
        "birthdate": player_dict.get("birthDate", "2000-01-01")
    })
    # Return the player object:
    return player

# SkaterOverallStats construct function used to build SkaterOverallStats objects. It accepts the player dictionary built by the roster_build nhl function and parses needed values from the JSON, returning a SkaterOverallStats object:
def skater_overall_stats_construct(player_stats:dict) -> SkaterOverallStats:
    # Initialize the SkaterOverallStats object with player_id from Player object:
    skater_overall_stats, _ = SkaterOverallStats.objects.update_or_create(player=Player.objects.get(player_id=player_stats["playerId"]), 
    # Parse the skater's season:
    season=player_stats.get("season", 20202021),
    defaults={
        # Parse the skater's games:
        "games": player_stats.get("games", 0),
        # Parse the skater's goals:
        "goals": player_stats.get("goals", 0),
        # Parse the skater's assists:
        "assists": player_stats.get("assists", 0),
        # Parse the skater's points:
        "points": player_stats.get("points", 0),
        # Parse the skater's penalty minutes:
        "pim": player_stats.get("pim", 0),
        # Parse the skater's +/- rating:
        "plusmin": player_stats.get("plusMinus", 0),
        # Parse the skater's time on ice per game:
        "toipg": player_stats.get("timeOnIcePerGame", "00:00"),
        # Parse the skater's powerplay goals:
        "ppg": player_stats.get("powerPlayGoals", 0),
        # Parse the skater's powerplay assists:
        "ppa": player_stats.get("powerPlayPoints", 0) - player_stats.get("powerPlayGoals", 0),
        # Parse the skater's shorthanded goals:
        "shg": player_stats.get("shortHandedGoals", 0),
        # Parse the skater's shorthanded assists:
        "sha": player_stats.get("shortHandedPoints", 0) - player_stats.get("shortHandedGoals", 0),
        # Parse the skater's even time on ice per game:
        "etoipg": player_stats.get("evenTimeOnIcePerGame", "00:00"),
        # Parse the skater's shorthanded time on ice per game:
        "shtoipg": player_stats.get("shortHandedTimeOnIcePerGame", "00:00"),
        # Parse the skater's powerplay time on ice per game:
        "pptoipg": player_stats.get("powerPlayTimeOnIcePerGame", "00:00"),
        # Parse the skater's shots:
        "shots": player_stats.get("shots", 0),
        # Parse the skater's shot percentage:
        "shotpct": player_stats.get("shotPct", 0),
        # Parse the skater's faceoff percentage:
        "fopct": player_stats.get("faceOffPct", 0),
        # Parse the skater's blocks:
        "blocks": player_stats.get("blocked", 0),
        # Parse the skater's hits:
        "hits": player_stats.get("hits", 0),
        # Parse the skater's shifts:
        "shifts": player_stats.get("shifts", 0),
        # Parse the skater's game winning goals:
        "gwg": player_stats.get("gameWinningGoals", 0)
    })
    # Return the skater_overall_stats object:
    return skater_overall_stats

# GoalieOverallStats construct function used to build GoalieOverallStats objects. It accepts the player dictionary built by the roster_build nhl function and parses needed values from the JSON, returning a GoalieOverallStats object:
def goalie_overall_stats_construct(goalie_stats:dict) -> GoalieOverallStats:
    # Initialize the GoalieOverallStats object with player_id from Player object:
    goalie_overall_stats, _ = GoalieOverallStats.objects.update_or_create(player=Player.objects.get(player_id=goalie_stats["playerId"]),
    # Parse the goalie's season:
    season=goalie_stats.get("season", 20202021),
    defaults={
        # Parse the goalie's games:
        "games": goalie_stats.get("games", 0),
        # Parse the goalie's wins:
        "wins": goalie_stats.get("wins", 0),
        # Parse the goalie's losses:
        "losses": goalie_stats.get("losses", 0),
        # Parse the goalie's ties:
        "ties": goalie_stats.get("ties", 0),
        # Parse the goalie's games started:
        "started": goalie_stats.get("gamesStarted", 0),
        # Parse the goalie's saves:
        "saves": goalie_stats.get("saves", 0),
        # Parse the goalie's shots against:
        "shotsa": goalie_stats.get("shotsAgainst", 0),
        # Parse the goalie's goals against:
        "goalsa": goalie_stats.get("goalsAgainst", 0),
        # Parse the goalie's time on ice per game:
        "toipg": goalie_stats.get("timeOnIcePerGame", "00:00"),
        # Parse the goalie's save percentage:
        "svpct": goalie_stats.get("savePercentage", 0),
        # Parse the goalie's goals against average:
        "gaa": goalie_stats.get("goalAgainstAverage", 0),
        # Parse the goalie's overtimes:
        "ot": goalie_stats.get("ot", 0),
        # Parse the goalie's shutouts:
        "shutouts": goalie_stats.get("shutouts", 0),
        # Parse the goalie's even strength saves:
        "essaves": goalie_stats.get("evenSaves", 0),
        # Parse the goalie's powerplay saves:
        "ppsaves": goalie_stats.get("powerPlaySaves", 0),
        # Parse the goalie's shorthanded saves:
        "shsaves": goalie_stats.get("shortHandedSaves", 0),
        # Parse the goalie's even strength shots against:
        "esshots": goalie_stats.get("evenShots", 0),
        # Parse the goalie's powerplay shots against:
        "ppshots": goalie_stats.get("powerPlayShots", 0),
        # Parse the goalie's shorthanded shots against:
        "shshots": goalie_stats.get("shortHandedShots", 0),
        # Parse the goalie's even strength save percentage:
        "essvpct": goalie_stats.get("evenStrengthSavePercentage", 0),
        # Parse the goalie's powerplay save percentage:
        "ppsvpct": goalie_stats.get("powerPlaySavePercentage", 0),
        # Parse the goalie's shorthanded save percentage:
        "shsvpct": goalie_stats.get("shortHandedSavePercentage", 0)
    })
    return goalie_overall_stats

# SkaterGameStats construct function used to build SkaterGameStats objects. It accepts the player dictionary built by the roster_build nhl function and parses needed values from the JSON, returning a SkaterGameStats object:
def skater_game_stats_construct(game_id:int, player_stats:dict) -> SkaterGameStats:
    # Initialize the SkaterGameStats object with game_id from Game object:
    skater_game_stats, _ = SkaterGameStats.objects.update_or_create(game=Game.objects.get(game_id=game_id), player=Player.objects.get(player_id=player_stats["playerId"]),
    defaults={
        # Parse the skater's goals:
        "goals": player_stats.get("goals", 0),
        # Parse the skater's assists:
        "assists": player_stats.get("assists", 0),
        # Parse the skater's points:
        "points": player_stats.get("goals", 0) + player_stats.get("assists", 0),
        # Parse the skater's penalty minutes:
        "pim": player_stats.get("penaltyMinutes", 0),
        # Parse the skater's +/- rating:
        "plusmin": player_stats.get("plusMinus", 0),
        # Parse the skater's time on ice per game:
        "toi": player_stats.get("timeOnIce", "00:00"),
        # Parse the skater's powerplay goals:
        "ppg": player_stats.get("powerPlayGoals", 0),
        # Parse the skater's powerplay assists:
        "ppa": player_stats.get("powerPlayAssists", 0),
        # Parse the skater's shorthanded goals:
        "shg": player_stats.get("shortHandedGoals", 0),
        # Parse the skater's shorthanded assists:
        "sha": player_stats.get("shortHandedAssists", 0),
        # Parse the skater's even time on ice per game:
        "etoi": player_stats.get("evenTimeOnIce", "00:00"),
        # Parse the skater's shorthanded time on ice per game:
        "shtoi": player_stats.get("shortHandedTimeOnIce", "00:00"),
        # Parse the skater's powerplay time on ice per game:
        "pptoi": player_stats.get("powerPlayTimeOnIce", "00:00"),
        # Parse the skater's shots:
        "shots": player_stats.get("shots", 0),
        # Parse the skater's blocks:
        "blocks": player_stats.get("blocked", 0),
        # Parse the skater's hits:
        "hits": player_stats.get("hits", 0),
        # Parse the skater's faceoff wins:
        "fow": player_stats.get("faceOffWins", 0),
        # Parse the skater's faceoffs taken:
        "fot": player_stats.get("faceoffTaken", 0),
        # Parse the skater's takeaways:
        "ta": player_stats.get("takeaways", 0),
        # Parse the skater's giveaways:
        "ga": player_stats.get("giveaways", 0)
    })
    # Return the skater_game_stats object:
    return skater_game_stats

# GoalieGameStats construct function used to build GoalieGameStats objects. It accepts the goalie_stats dictionary built by the game_stats_individual_build nhl function and parses needed values from the JSON, returning a GoalieGameStats object:
def goalie_game_stats_construct(game_id:int, goalie_stats: dict) -> GoalieGameStats:
    # Initialize the GoalieGameStats object with game_id from Game object:
    goalie_game_stats, _ = GoalieGameStats.objects.update_or_create(game=Game.objects.get(game_id=game_id), 
    # Parse the skater's season:
    player=Player.objects.get(player_id=goalie_stats["playerId"]),
    defaults={
        # Parse the goalie's decision:
        "wl": goalie_stats.get("decision", "NA") if goalie_stats['decision'] == "W" or goalie_stats['decision'] == "L" else "NA",
        # Parse the goalie's goals against:
        "goalsa": goalie_stats.get("shots", 0) - goalie_stats.get("saves", 0),
        # Parse the goalie's shots against:
        "shotsa": goalie_stats.get("shots", 0),
        # Parse the goalie's saves:
        "saves": goalie_stats.get("saves", 0),
        # Parse the goalie's save percentage:
        "svpct": goalie_stats.get("savePercentage", 0),
        # Parse the goalie's time on ice:
        "toi": goalie_stats.get("timeOnIce", "00:00"),
        # Parse the goalie's penalty minutes:
        "pim": goalie_stats.get("pim", 0),
        # Parse the goalie's goals:
        "goals": goalie_stats.get("goals", 0),
        # Parse the goalie's assists:
        "assists": goalie_stats.get("assists", 0),
        # Parse the goalie's even strength saves:
        "essaves": goalie_stats.get("evenSaves", 0),
        # Parse the goalie's powerplay saves:
        "ppsaves": goalie_stats.get("powerPlaySaves", 0),
        # Parse the goalie's shorthanded saves:
        "shsaves": goalie_stats.get("shortHandedSaves", 0),
        # Parse the goalie's even strength shots against:
        "esshots": goalie_stats.get("evenShotsAgainst", 0),
        # Parse the goalie's powerplay shots against:
        "ppshots": goalie_stats.get("powerPlayShotsAgainst", 0),
        # Parse the goalie's shorthanded shots against:
        "shshots": goalie_stats.get("shortHandedShotsAgainst", 0),
        # Parse the goalie's even strength save percentage:
        "essvpct": goalie_stats.get("evenStrengthSavePercentage", 0),
        # Parse the goalie's powerplay save percentage:
        "ppsvpct": goalie_stats.get("powerPlaySavePercentage", 0),
        # Parse the goalie's shorthanded save percentage:
        "shsvpct": goalie_stats.get("shortHandedSavePercentage", 0)
    })
    #shsvpct=goalie_stats["shortHandedSaves"]/(goalie_stats["shortHandedSaves"] + goalie_stats["shortHandedShots"]))
    return goalie_game_stats

# Games update function used to build the schedule, iterate through the games, create/update each Game object, and make changes the database:
def games_update(season:int):
    # Build the schedule using the nhl.schedule_build function:
    schedule = nhl.schedule_build(nhl.schedule_url, nhl.game_score_url, season)
    # Iterate through the schedule dictionary by game:
    for _, val in schedule.items():
        # Construct the Game object from the game's attributes:
        g = game_construct(val)
        # Save the object to the database:
        g.save()

# Players update function used to iterate through the roster, create/update each Player object, and make changes the database:
def players_update():
    # Iterate through the roster dictionary by player:
    for _, val in roster.items():
        # Construct the Player object from the player's attributes:
        p = player_construct(val)
        # Save the object to the database:
        p.save()

# SkaterOverallStats update function used to build the overall stats, iterate through the stats by skater, create/update each SkaterOverallStats object, and make changes to the database:
def skater_overall_stats_update(season:int):
    # Build the overall stats using the nhl.overall_stats_total_build function:
    overall_stats = nhl.overall_stats_total_build(roster, nhl.player_overall_stats_url, season)
    # Iterate through the overall_stats dictionary by skater:
    for _, val in overall_stats["skater_stats"].items():
        # Construct the SkaterOverallStats object from the skater's attributes:
        s = skater_overall_stats_construct(val)
        # Save the object to the database:
        s.save()

# GoalieOverallStats update function used to build the overall stats, iterate through the stats by goalie, create/update each GoalieOverallStats object, and make changes to the database:
def goalie_overall_stats_update(season:int):
    # Build the overall stats using the nhl.overall_stats_total_build function:
    overall_stats = nhl.overall_stats_total_build(roster, nhl.player_overall_stats_url, season)
    # Iterate through the overall_stats dictionary by goalie:
    for _, val in overall_stats["goalie_stats"].items():
        # Construct the SkaterOverallStats object from the goalie's attributes:
        g = goalie_overall_stats_construct(val)
        # Save the object to the database:
        g.save()

def game_stats_update(game_id:int):
    game_stats = nhl.game_stats_total_build(game_id, nhl.game_stats_url)
    for _, val in game_stats.items():
        s = Player.objects.get(player_id=val["playerId"])
        if (s.position == "Goalie"):
            p = goalie_game_stats_construct(game_id, val)
        else:
            p = skater_game_stats_construct(game_id, val)
        p.save()
        
# Run function needed for the runscripts extension to execute:
def run():
    print("Updating Schedule")
    games_update(20202021)
    print("Updating Roster")
    players_update()
    print("Updating Overall Stats")
    skater_overall_stats_update(20202021)
    goalie_overall_stats_update(20202021)
    print("Updating Game Stats")
    for x in Game.objects.values():
        if (x["played"] == True):
            game_stats_update(x["game_id"])
