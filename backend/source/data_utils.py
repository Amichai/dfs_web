from tinydb import TinyDB, Query, where
import utils

DB_ROOT = 'DBs/'
SCRAPE_OPERATIONS_TABLE = 'scrape_operations'

def get_scraped_lines(scraper):
    file_most_recent = open('DBs/{}/{}_current.txt'.format('NBA', scraper), 'r')

    all_results = []
    lines = file_most_recent.readlines()
    time = lines[0]
    keys = lines[1].split(',')
    rows = lines[2:]

    for row in rows:
      obj = {}
      for idx in range(len(keys)):
          key = keys[idx].strip()
          row_parts = row.split(',')
          val = row_parts[idx]

          obj[key] = val

      all_results.append(obj)

    return all_results


def write_slate(sport, slate_id, site, date, columns, player_data, game_data):
    filepath = 'DBs/{}/slates_{}.txt'.format(sport, date)
    file = open(filepath, 'a')
    file.write('slate: {} site: {}\n'.format(slate_id, site))
    file.write('game data: {}\n'.format(game_data))
    file.write('columns: {}\n'.format(','.join(columns)))
    for player in player_data:
        file.write('{}\n'.format(','.join(player)))
    pass

def get_slate_players(sport, site, slate_id, date):
    filepath = 'DBs/{}/slates_{}.txt'.format(sport, date)
    file = open(filepath, 'r')

    players = []

    start_idx_key = 'slate: {} site: {}\n'.format(slate_id, site)
    lines = file.readlines()
    index = len(lines) - 1 - lines[::-1].index(start_idx_key)
    columns = None
    game_data = None
    while True:
        index += 1
        if index >= len(lines):
            break
        line = lines[index]

        if 'slate: ' in line:
            break
        elif 'game data: ' in line:
            game_data = line.replace('game data: ', '').strip().replace(',', '\n')
            continue
        elif 'columns: ' in line:
            columns = line.replace('columns: ', '').strip().split(',')
            continue
        else:
            player = line.strip().split(',')
            player = {k: v for k,v in zip(columns, player)}
            
            players.append(player)
   
    return players, game_data


def get_scraped_lines_multiple(projection_sources):
  scraped_lines = []
  for source in projection_sources:
    scraped_lines += get_scraped_lines(source)
    print(len(scraped_lines))

  return scraped_lines


def get_slate_players_and_teams(site, sport, slate_id, exclude_injured=True):
    slate_players, _ = get_slate_players(sport, site, slate_id, utils.date_str())


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


def add_casesar_projections(name_stat_to_val, all_names, site='fd'):
    get_key = lambda a, b: "{}_{}".format(a, b)
    key_generators = [
        lambda a: get_key(a, 'Points'),
        lambda a: get_key(a, 'Assists'),
        lambda a: get_key(a, 'Rebounds'),
        lambda a: get_key(a, 'Blocks'),
        lambda a: get_key(a, 'Steals'),
        lambda a: get_key(a, 'Turnovers'),
        lambda a: get_key(a, '3pt Field Goals'),
    ]

    for name in all_names:
        stat_vals = []
        for key_generator in key_generators:
            key = key_generator(name)
            if key in name_stat_to_val:
                stat_vals.append(float(name_stat_to_val[key]))
            else:
                stat_vals.append(0)

        if sum(stat_vals) > 0:
            turnover_penalty = stat_vals[5] / 3
            if site == 'dk':
                turnover_penalty /= 2
            val = stat_vals[0] + stat_vals[1] * 1.5 + stat_vals[2] * 1.2 + stat_vals[3] * 3 + stat_vals[4] * 3 - turnover_penalty

            if site == 'dk':
                val += stat_vals[6] * 0.5
            
            name_stat_to_val["{}_{}".format(name, 'CaesarsComputed')] = round(val, 3)


def get_current_projections(sport):
    lines = get_scraped_lines('Caesars_NBA')
    name_stat_to_val = {}
    all_names = []
    for line in lines:
        name = line['name']
        if not name in all_names:
            all_names.append(name)
        
        stat = line['stat']
        projection = line['line_score']

        name_stat_to_val["{}_{}".format(name, stat)] = projection
        pass

    add_casesar_projections(name_stat_to_val, all_names)

    to_return = {}

    for name in all_names:
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