from tinydb import TinyDB, Query, where
import utils

DB_ROOT = 'DBs/'
SCRAPE_OPERATIONS_TABLE = 'scrape_operations'


# test code only...
def get_scraped_lines_for_date(scraper, date, sport='NBA'):
    file = open('DBs/{}/{}_{}.txt'.format(sport, scraper, date), 'r')
    lines = file.readlines()
    indices = []
    for i in range(len(lines)):
        if lines[i].startswith('t:'):
            indices.append(i)
            
    last_idx = indices[-1]
    lines = lines[last_idx:]
    return lines

def get_scraped_lines_historical(scraper, sport, date):
    file = open('DBs/{}/{}_{}.txt'.format(sport, scraper, date), 'r')
    name_stat_to_obj = {}
    key_line = 'line_score,stat,start_time,line_original,under_fraction,over_fraction,active,name,team'
    keys = key_line.split(',')
    
    lines = file.readlines()
    for line in lines:
        if key_line in line:
            continue
        line = line.strip()
        parts = line.split(',')
        if len(parts) < 8:
            continue
        obj = {}
        for idx in range(len(keys)):
            key = keys[idx].strip()
            row_parts = line.split(',')
            val = row_parts[idx]
            obj[key] = val
        name = parts[7]
        stat = parts[1]
        name_stat_to_obj['{}_{}'.format(name, stat)] = obj
        
    to_return = list(name_stat_to_obj.values())
    return to_return

def get_scraped_lines(scraper, sport='NBA'):
    file_most_recent = open('DBs/{}/{}_current.txt'.format(sport, scraper), 'r')

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


def scraped_lines_to_projections(lines, site='fd'):
    name_to_stat_to_val = {}
    for line in lines:
        if line.startswith('t:'):
            continue
        parts = line.split(',')
        name = parts[7]
        stat = parts[1]
        val = parts[0]
        if not name in name_to_stat_to_val:
            name_to_stat_to_val[name] = {}
        name_to_stat_to_val[name][stat] = val

    name_to_projection = {}
    for name, stats in name_to_stat_to_val.items():
        pts, assists, rebounds, blocks, steals, turnovers, three_pointers = 0, 0, 0, 0, 0, 0, 0
        
        if 'Points' in stats:
            pts = float(stats['Points'])
            
        if 'Assists' in stats:
            assists = float(stats['Assists'])
        
        if 'Rebounds' in stats:
            rebounds = float(stats['Rebounds'])
        
        if 'Blocks' in stats:
            blocks = float(stats['Blocks'])
    
        if 'Steals' in stats:
            steals = float(stats['Steals'])
        
        if 'Turnovers' in stats:
            turnovers = float(stats['Turnovers'])
        
        if '3pt Field Goals' in stats:
            three_pointers = float(stats['3pt Field Goals'])
        
        projection = compute_caesar_projection(pts, assists, rebounds, blocks, steals, turnovers, three_pointers, site)
        name_to_projection[name] = round(projection, 3)
        
    return name_to_projection

def get_caesars_projection_history():
    date_string = utils.date_str()
    try:
        file_today = open('DBs/{}/{}_{}.txt'.format('NBA', 'Caesars', date_string), 'r')
    except:
        return []
    
    header_row = 'line_score,stat,start_time,line_original,under_fraction,over_fraction,active,name,team'
    
    all_scrapes = []
    current_scrape = []
    current_scrape_time = None
    
    all_lines = file_today.readlines()
    print(len(all_lines))
    for line in all_lines:
        if line.startswith('t:'):
            if current_scrape_time != None:
                projections = scraped_lines_to_projections(current_scrape)
                all_scrapes.append({
                    'time': current_scrape_time,
                    'projections': projections
                })
            
            current_scrape_time = line.split(' ')[1].strip()
            current_scrape = []
            continue
        if header_row in line:
            continue
        
        current_scrape.append(line)
    
    projections = scraped_lines_to_projections(current_scrape)
    all_scrapes.append({
        'time': current_scrape_time,
        'projections': projections
    })
    name_to_projections = {}
    for scrape in all_scrapes:
        projections = scrape['projections']
        time = scrape['time']
        for name, projection in projections.items():
            if not name in name_to_projections:
                name_to_projections[name] = []
            name_to_projections[name].append((time, projection))
    
    
    name_to_projection_history = {}
    for name, projections in name_to_projections.items():
        projections.reverse()
        
        most_recent_projection = projections[0]
        current_projection = most_recent_projection[1]
        last_update = most_recent_projection[0]
        max_projection = max(projections, key=lambda a: a[1])
        min_projection = min(projections, key=lambda a: a[1])
        proj_inspection = most_recent_projection
        last_change = None
        last_change_diff = None
        for projection in projections:
            if abs(proj_inspection[1] - projection[1]) > .1:
                last_change = proj_inspection[0]
                last_change_diff = round(proj_inspection[1] - projection[1], 3)
                
            proj_inspection = projection
        
        name_to_projection_history[name] = {
            'current': current_projection,
            'last_update': last_update,
            'max': max_projection[1],
            'min': min_projection[1],
            'last_change': last_change,
            'last_change_diff': last_change_diff 
        }

    print(name_to_projection_history)


def write_slate(sport, slate_id, site, date, columns, player_data, game_data):
    filepath = 'DBs/{}/slates_{}.txt'.format(sport, date)
    file = open(filepath, 'a')
    file.write('slate: {} site: {}\n'.format(slate_id, site))
    file.write('game data: {}\n'.format(game_data))
    file.write('columns: {}\n'.format(','.join(columns)))
    for player in player_data:
        file.write('{}\n'.format(','.join(player)))
    pass

def get_slates(sport, site, date):
    print('get_slates', sport, site, date)
    filepath = 'DBs/{}/slates_{}.txt'.format(sport, date)
    file = open(filepath, 'r')
    lines = file.readlines()
    slate_ids = {}
    site_key = 'site: {}'.format(site)
    for line in lines:
        if 'slate: ' in line and site_key in line:
            slate_id = line.replace('slate: ', '').split(' ')[0]
            print(slate_id)
            
            players, game_data = get_slate_players(sport, site, slate_id, date)
            # slate_ids.append(slate_id)
            # import pdb; pdb.set_trace()
            seen_games = []
            for player in players:
                game = player['game']
                if not game in seen_games:
                    seen_games.append(game)
            
            game_type = 'single_game' if len(seen_games) == 1 else ''
            
            start_time = 11.8
            if game_data != '':
                start_time_string = game_data.split(' ')[0].split('\n')[-1]
                start_time = utils.convert_time_string_to_decimal(start_time_string)
            
            slate_ids[slate_id] = {
                'sport': sport,
                'site': site,
                'type': game_type,
                'name': slate_id,
                'start_time': start_time,
            }

    # I want to return a dictionary of slateId to ->
    # sport, site, type, name, start time

    return slate_ids

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


def get_slate_players_and_teams(site, sport, slate_id, exclude_injured=True, date=None):
    if date == None:
        date = utils.date_str()
    slate_players, _ = get_slate_players(sport, site, slate_id, date)

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


def compute_caesar_projection(points, assists, rebounds, blocks, steals, turnovers, three_pointers, site='fd'):
    if site == 'fd':
        val = points + assists * 1.5 + rebounds * 1.2 + blocks * 3 + steals * 3 - (turnovers / 3.0)
        
    elif site == 'dk':
        val = points + assists * 1.5 + rebounds * 1.25 + blocks * 2 + steals * 2 - (turnovers / 6.0) + (three_pointers * 0.5)
        
    else:
        assert False
        
    return val

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
            val = compute_caesar_projection(stat_vals[0], stat_vals[1], stat_vals[2], stat_vals[3], stat_vals[4], stat_vals[5], stat_vals[6], site)
            
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