from tinydb import TinyDB, Query, where
import utils

DB_ROOT = 'DBs/'
SCRAPE_OPERATIONS_TABLE = 'scrape_operations'

def get_scraped_lines(scraper):
    query = Query()
    db = TinyDB(DB_ROOT + SCRAPE_OPERATIONS_TABLE)
    results = db.search(query['scraper'] == scraper)

    results_sorted = sorted(results, key=lambda a: a['scrape_time'])
    if len(results_sorted) == 0:
        return []
    most_recent_scrape = results_sorted[-1]

    query2 = Query()
    db2 = TinyDB(DB_ROOT + scraper)

    all_results = db2.search(query2['time'] == most_recent_scrape['scrape_time'])

    return all_results

def get_scraped_lines_multiple(projection_sources):
  scraped_lines = []
  for source in projection_sources:
    scraped_lines += get_scraped_lines(source)
    print(len(scraped_lines))

  return scraped_lines


def get_slate_players_and_teams(table_root, sport, slate_id, exclude_injured=True):
    db = TinyDB(DB_ROOT + table_root + sport)
    query = Query()
    slate_players = db.search((query['slateId'] == slate_id))

    if exclude_injured:
      slate_players = [a for a in slate_players if a['injury'] != 'O']

    team_list = []
    for player in slate_players:
        team = player['team']
        if not team in team_list:
            team_list.append(team)

    name_to_id = utils.name_to_player_id(slate_players)

    return slate_players, team_list, name_to_id

def get_most_recent_slate(sport):
    db = TinyDB(DB_ROOT + "slates")
    query = Query()
    upcoming_slates = db.search(query['sport'] == sport)
    most_recent_slate = upcoming_slates[-1]
    return most_recent_slate


def add_casesar_projections(name_stat_to_val, all_names):
    get_key = lambda a, b: "{}_{}".format(a, b)
    key_generators = [
        lambda a: get_key(a, 'Points'),
        lambda a: get_key(a, 'Assists'),
        lambda a: get_key(a, 'Rebounds'),
        lambda a: get_key(a, 'Blocks'),
        lambda a: get_key(a, 'Steals'),
        lambda a: get_key(a, 'Turnovers'),
    ]

    for name in all_names:
        stat_vals = []
        for key_generator in key_generators:
            key = key_generator(name)
            if key in name_stat_to_val:
                stat_vals.append(name_stat_to_val[key])
            else:
                stat_vals.append(0)

        if sum(stat_vals) > 0:
            val = stat_vals[0] + stat_vals[1] * 1.5 + stat_vals[2] * 1.2 + stat_vals[3] * 3 + stat_vals[4] * 3 - (stat_vals[5] / 3)
            name_stat_to_val["{}_{}".format(name, 'CaesarsComputed')] = round(val, 3)

def get_current_projections(sport):
  scraped_lines = get_scraped_lines_multiple(['PrizePicks_' + sport, 'Caesars_' + sport])
  seen_names = []
  seen_stats = []

  name_to_stats = {}
  name_stat_to_val = {}

  for result in scraped_lines:
      name = result['name']
      line = result['line_score']
      team = result['team']
      stat = result['stat']
      
      if not name in name_to_stats:
          name_to_stats[name] = [stat]
      else:
          name_to_stats[name].append(stat)

      name_stat = "{}_{}".format(name, stat)
      name_stat_to_val[name_stat] = line

      if not name in seen_names:
          seen_names.append(name)

      if not stat in seen_stats:
          seen_stats.append(stat) 

  add_casesar_projections(name_stat_to_val, seen_names)
  to_return = {}


  for name in seen_names:
      key1 = "{}_{}".format(name, "Fantasy Score")
      key2 = "{}_{}".format(name, "CaesarsComputed")
      proj = None
      if key1 in name_stat_to_val:
          proj = name_stat_to_val[key1]

      if key2 in name_stat_to_val:
          proj = name_stat_to_val[key2]

      if proj != None:
        to_return[name] = proj


  return to_return