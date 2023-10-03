from name_mapper import name_mapper_pp_to_fd_dk, name_mapper
from tinydb import Query
import utils
from optimizer_library import DK_NBA_Optimizer, NFL_Optimizer
import itertools

def normalize_name(name):
    if name in name_mapper:
        name = name_mapper[name]

    return name


def _get_player_pool(name_stat_to_val, seen_names, slate_lines, site):
  player_pool = []

  for name in seen_names:
      unmapped_name = name
      if name in name_mapper_pp_to_fd_dk:
          name = name_mapper_pp_to_fd_dk[name]

      if 'DST' in name:
          parsed_name = name.split(' ')[0]
          matched_names = [a for a in slate_lines if parsed_name in a['name']]
      else:
          matched_names = [a for a in slate_lines if a['name'] == name]

        
      if len(matched_names) == 0:
          if not '+' in name:
            print("Missing projection for: ", name)
          continue
      
      if len(matched_names) > 1:
        salary1 = float(matched_names[0]['salary'])
        salary2 = float(matched_names[1]['salary'])
        salary = min(salary1, salary2)
        assert len(matched_names) == 2
      else:
        salary = float(matched_names[0]['salary'])


      position = matched_names[0]['position']
      team = matched_names[0]['team']
      
      proj = None

      key1 = "{}_{}".format(unmapped_name, "Fantasy Score")
      key2 = "{}_{}".format(unmapped_name, "FSComputed")
      if key1 in name_stat_to_val:
          proj = name_stat_to_val[key1]
      if key2 in name_stat_to_val:
          proj = name_stat_to_val[key2]

      if proj is None:
          key3 = "{}_{}".format(unmapped_name, "FSInferred")
          if key3 in name_stat_to_val:
            proj = name_stat_to_val[key3]


      if proj is None:
          continue
      
      # print("{},{},{}".format(name, salary, proj))
      # fantasy_score = 
      # get the player cost

      player_pool.append([name, salary, proj, position, team])
  return player_pool

def get_player_projection_data(scraped_lines, teams_to_include, computed_stats=[]):
    seen_names = []
    seen_stats = []

    name_to_stats = {}
    name_stat_to_val = {}

    for result in scraped_lines:
        name = result['name']
        line = result['line_score']
        team = result['team']
        stat = result['stat']
        if teams_to_include and team not in teams_to_include:
            continue
        
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


    for name, stats in name_to_stats.items():
        for computed_stat in computed_stats:
          computed_stat_name = computed_stat['name']
          if all([a in stats for a in computed_stat['stats']]):
              new_stat_name = "{}_{}".format(name, computed_stat_name)
              new_val = 0
              for i, stat in enumerate(computed_stat['stats']):
                  new_val += name_stat_to_val["{}_{}".format(name, stat)] * computed_stat['weights'][i]

              name_stat_to_val[new_stat_name] = new_val

              if not computed_stat_name in seen_stats:
                  seen_stats.append(computed_stat_name)

    print('', end=',')
    for stat in seen_stats:
        print(stat, end=',')
    print()

    for name in seen_names:
        print(name, end=',')
        for stat in seen_stats:
            name_stat = "{}_{}".format(name, stat)
            if name_stat in name_stat_to_val:
                print(name_stat_to_val[name_stat], end=',')
            else:
                print('', end=',')
        print()

    return name_stat_to_val, seen_names, seen_stats





def get_player_projection(scraped_lines, name):
    matched_players = [a for a in scraped_lines if a['name'].strip() == name]
    if len(matched_players) == 0:
        print("Missing projection for: ", name)
        return 0

    try:
        pts = [a for a in matched_players if a['stat'] == 'Points'][0]['line_score']
        # rebounds = [a for a in matched_players if a['stat'] == 'Rebounds'][0]['line_score']
    except:
        print("insufficient data for: ", name)
        return 0
    
    return float(pts)
    # return float(pts) + float(rebounds) * 1.5


def optimize_for_single_game_fd(all_players, ct, locks=None):
    all_rosters = []

    roster_keys = set()

    candidates = itertools.permutations(all_players, 5)
    for candidate in candidates:
        total_cost = sum(pl[1] for pl in candidate)
        if total_cost > 60000:
            continue
        
        p1 = candidate[0]
        p2 = candidate[1]
        p3 = candidate[2]
        p4 = candidate[3]
        p5 = candidate[4]
        all_players = [p1, p2, p3, p4, p5]
        seen_teams = []
        for p in all_players:
            team = p[4]
            if not team in seen_teams:
                seen_teams.append(team)

        if len(seen_teams) == 1:
            continue

        total_value = p1[2] * 1.5 + p2[2]+  p3[2] + p4[2] + p5[2]

        roster_key = "|".join(sorted([a[0] for a in candidate])) + "|" + str(round(total_value, 5))
        if roster_key in roster_keys:
            continue

        roster_keys.add(roster_key)
        all_rosters.append((candidate, total_value, total_cost))

    all_rosters_sorted = sorted(all_rosters, key=lambda a: a[1], reverse=True)
    to_return = all_rosters_sorted[:ct]
    for roster in to_return:
        print(roster)
        
    return to_return


def optimize_FIBA_dk(slate_players, scraped_lines):
    dk_positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

    # print(results)
    by_position = {}
    for slate_player in slate_players:
        # print(slate_player)
        name = slate_player['name'].strip()
        name = normalize_name(name)
        positions = slate_player['position'].split('/')
        salary = slate_player['salary']
        team = slate_player['team']
        projection = get_player_projection(scraped_lines, name)
        
        # projection += float(salary) / 11800 # prefer higher salary
        # projection += random.uniform(0, 1) / 1000 #this is necessary apparently
        if projection == 0:
            continue

        all_position = []

        for position in positions:
            # if not position in by_position:
            #     by_position[position] = []
            positions_extended = dk_positions_mapper[position]
            for pos in positions_extended:
                if not pos in all_position:
                    all_position.append(pos)
        
        for pos in all_position:
            if not pos in by_position:
                by_position[pos] = []
            
            by_position[pos].append(utils.Player(name, position, salary, team, projection))

    optimizer = DK_NBA_Optimizer()

    results = optimizer.optimize(by_position, None)

    print(results)


    return results


computed_stats = [
    # {
    #   'name': 'FSComputed', # for QBs missing a fantasy score
    #   'stats': ['Pass Yards', 'Pass TDs', 'Rush Yards'],
    #   'weights': [0.04, 4, 0.1]
    # },
    # {
    #   'name': 'FSComputed', # for QBs missing a fantasy score
    #   'stats': ['Pass Yards', 'Pass+Rush+Rec TDs', 'Rush Yards'],
    #   'weights': [0.04, 4, 0.1]
    # },
    {
    'name': 'FSComputed',
    'stats': ['Fantasy Score', 'Receptions'],
    'weights': [1, -0.5]
    },
    {
    'name': 'FSInferred', # TODO: WE ONLY WANT TO APPLY THIS IF NO FANTASY SCORE VALUE IS PROVIDED!
    'stats': ['Kicking Points'],
    'weights': [1]
    },
    {
    'name': 'FSInferred',
    'stats': ['Receiving Yards', 'Receptions'],
    'weights': [0.1, 0.5]
    },
    {
    'name': 'FSInferred',
    'stats': ['Rush+Rec Yds', 'Receptions'],
    'weights': [0.1, 0.5]
    },
]

def get_player_pool(slate_players, scraped_lines, site, team_filter=None):
    computed_stats_to_pass = []
    if site == 'fd':
        computed_stats_to_pass = computed_stats
    else:
        computed_stats_to_pass = [computed_stats[1]]

    name_stat_to_val, seen_names, seen_stats = get_player_projection_data(scraped_lines, team_filter, computed_stats=computed_stats_to_pass)

    player_pool = _get_player_pool(name_stat_to_val, seen_names, slate_players, site)

    return player_pool

def print_slate_new(slate_players, player_pool, site, teams):
    for team in teams:
        print("-----------------")
        print(team)
        print("-----------------")
        if site == 'dk' and team == 'JAC':
            team = 'JAX'
        slate_players1 = [a for a in slate_players if a['team'] == team]
        players_sorted = sorted(slate_players1, key=lambda a: int(a['salary']), reverse=True)
        for player in players_sorted:
            name = player['name']
            position = player['position']

            if position == 'DST' and site == 'dk':
                name = name + position

            matched = [a for a in player_pool if a[0] == name]
            projected = ''
            if len(matched) == 1:
                projected = matched[0][2]
            elif len(matched) > 1:
                print("error name matched multiple times")
                assert False

            salary = player['salary']
            
            cuttoff_salary = 4000
            if site == 'fd':
                cuttoff_salary = 4500

            # if 'DST' in position:
            #     import pdb; pdb.set_trace()
            if float(salary) >= cuttoff_salary or 'DST' in position:
                print(name, salary, position, projected)


def print_slate(slate_players, player_pool, slate_games, site):
    team_to_start_time = {}
    lines = slate_games.split('\n')
    teams_in_order = []
    print(lines)
    for i in range(len(lines)):
        if lines[i] == '':
            continue
        if lines[i][0] == '@':
            team1 = lines[i - 1]
            team2 = lines[i].strip('@')
            timeString1 = lines[i + 1]
            timeString2 = ''
            if len(lines) > i + 2:
                timeString2 = lines[i + 2]

            team_to_start_time[team1] = "{} {}".format(timeString1, timeString2)
            team_to_start_time[team2] = "{} {}".format(timeString1, timeString2)
            teams_in_order.append(team1)
            teams_in_order.append(team2)


    for team in teams_in_order:
        print("-----------------")
        print(team, team_to_start_time[team])
        print("-----------------")
        if site == 'dk' and team == 'JAC':
            team = 'JAX'
        slate_players1 = [a for a in slate_players if a['team'] == team]
        players_sorted = sorted(slate_players1, key=lambda a: a['salary'], reverse=True)
        for player in players_sorted:
            name = player['name']
            position = player['position']

            if position == 'DST' and site == 'dk':
                name = name + position

            matched = [a for a in player_pool if a[0] == name]
            projected = ''
            if len(matched) == 1:
                projected = matched[0][2]
            elif len(matched) > 1:
                print("error name matched multiple times")
                assert False

            salary = player['salary']
            
            cuttoff_salary = 4000
            if site == 'fd':
                cuttoff_salary = 4500

            # if 'DST' in position:
            #     import pdb; pdb.set_trace()
            if float(salary) >= cuttoff_salary or 'DST' in position:
                print(name, salary, position, projected)

        # team_players = [a for a in player_pool if a[4] == team]
        # for player in team_players:
        #     print(player)
        # print()
    # PARSE THE GAME TIMES
    # SORT BY GAME TIME
    # FOR EACH TEAM, SORT PLAYERS BY COST
    # print("PRINT SLATE")
    # for player in slate_players:
    #     print(player)


def reoptimize_fd_nfl(player_pool, iterCount, rosters):
    by_position = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'FLEX': [], 'D': []}

    for player in player_pool:
        name = player[0]
        cost = player[1]
        proj = player[2]
        position = player[3]
        team = player[4]
        player = utils.Player(name, player, cost, team, proj)

        by_position[position].append(player)
        if position != 'D' and position != 'QB':
            by_position['FLEX'].append(player)


    print(by_position)

    optimizer = NFL_Optimizer()
    results = []

    for locks in rosters:
        roster = optimizer.optimize(by_position, locks, iterCount * 10000)

        results += [roster]
    
    print(results)
    return results


def optimize_fd_nfl(player_pool, ct, iterCount):
    by_position = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'FLEX': [], 'D': []}

    for player in player_pool:
        name = player[0]
        cost = player[1]
        proj = player[2]
        position = player[3]
        team = player[4]
        player = utils.Player(name, player, cost, team, proj)

        by_position[position].append(player)
        if position != 'D' and position != 'QB':
            by_position['FLEX'].append(player)


    print(by_position)

    optimizer = NFL_Optimizer()
    # optimizer.optimize(by_position, None, 100000)
    results = optimizer.optimize_top_n(by_position, ct, iterCount * 10000)
    print(results)
    return results

def optimize_dk_nfl(player_pool):
    print(player_pool)

    by_position = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'FLEX': [], 'D': []}

    for player in player_pool:
        name = player[0]
        cost = player[1]
        proj = player[2]
        position = player[3]
        if position == 'DST':
            position = 'D'
        team = player[4]
        player = utils.Player(name, player, cost, team, proj)

        by_position[position].append(player)
        if position != 'D' and position != 'QB':
            by_position['FLEX'].append(player)



    optimizer = NFL_Optimizer(50000)
    # optimizer.optimize(by_position, None, 100000)
    results = optimizer.optimize_top_n(by_position, 20, 130000)
    print(results)
    return results