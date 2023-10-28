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