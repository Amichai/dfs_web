import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')

import utils
import time
from datetime import date

known_sports = ["NBA", "MLB", "WNBA", "NFL", "NFLP", "MMA", "CFB", "NASCAR", "NHL", "CBB", "FIBA"]

class PPScraper:
  def __init__(self, sport):
    self.sport = sport
    self.name = 'PP'

    assert sport in known_sports

  def run(self, scrape_time):
    league_id = None
    if self.sport == "NBA":
      league_id = 7
    elif self.sport == "WNBA":
      league_id = 3
    elif self.sport == "NFL":
      league_id = 9
    elif self.sport == "MLB":
      league_id = 2
    elif self.sport == "NFLP":
      league_id = 44
    elif self.sport == "MMA":
      league_id = 12
    elif self.sport == "CFB":
      league_id = 15
    elif self.sport == "CBB":
      league_id = 20
    elif self.sport == "NASCAR":
      league_id = 4
    elif self.sport == "NHL":
      league_id = 8
    elif self.sport == "FIBA":
      league_id = 185


    assert league_id != None
    url = 'https://api.prizepicks.com/projections?league_id={}&per_page=500&single_stat=false'.format(league_id)

    as_json = utils.get_with_selenium(url)

    assert as_json["meta"]["total_pages"] == 1

    data = as_json['data']
    included = as_json['included']

    id_to_name_team = {}
    player_ids = []
    for player in included:
        attr = player["attributes"]
        player_name = attr['name']
        team = ''
        if 'team' in attr:
          team = attr['team']
        
        player_id = player['id']
        player_ids.append(player_id)
        id_to_name_team[player_id] = (player_name, team)

    projections = []

    for projection in data:
        attr = projection['attributes']
        stat_type = attr['stat_type']
        start_time = attr['start_time']
        # created_at = attr["created_at"]
        board_time = attr["board_time"]
        updated_at = attr["updated_at"]
        is_promo = attr['is_promo']
        line_score = float(attr["line_score"])
        player_id = projection['relationships']['new_player']['data']['id']
        (player_name, team) = id_to_name_team[player_id]

        projections.append({
            "line_score": line_score,
            "updated_at": updated_at,
            "stat": stat_type,
            "start_time": start_time,
            "player_id": player_id,
            "team": team,
            "name": player_name,
            "time": scrape_time,
            "line_id": "{}_{}_{}".format(player_id, stat_type, start_time)
        })
        
    return projections
