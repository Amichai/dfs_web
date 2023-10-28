from name_mapper import name_mapper_pp_to_fd_dk, name_mapper_pp_to_fd, name_mapper
import utils
from optimizer_library import DK_NBA_Optimizer, NFL_Optimizer, FD_NBA_Optimizer
import itertools
from tabulate import tabulate
import data_utils
import datetime

def normalize_name(name):
    if name in name_mapper:
        name = name_mapper[name]

    return name

def _add_casesar_projections(name_stat_to_val, all_names):
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


def _get_player_pool(name_stat_to_val, seen_names, slate_lines, site, to_exclude):
  player_pool = []

  _add_casesar_projections(name_stat_to_val, seen_names)

  for name in seen_names:
      unmapped_name = name
      if name in name_mapper_pp_to_fd_dk:
          name = name_mapper_pp_to_fd_dk[name]
    
      elif site == 'fd' and name in name_mapper_pp_to_fd:
          name = name_mapper_pp_to_fd[name]

      if 'DST' in name:
          parsed_name = name.split(' ')[0]
          matched_names = [a for a in slate_lines if parsed_name in a['name']]
      else:
          matched_names = [a for a in slate_lines if a['name'] == name]

        
      if len(matched_names) == 0:
          if not '+' in name:
            print("Can't find target to apply projection for (excluded or injured?): ", name)
          continue
      
      if len(matched_names) > 1:
        salary1 = float(matched_names[0]['salary'])
        salary2 = float(matched_names[1]['salary'])
        salary = min(salary1, salary2)
        assert len(matched_names) == 2
      else:
        salary = float(matched_names[0]['salary'])


      position = matched_names[0]['position']

    #   print(position)

      team = matched_names[0]['team']
      
      proj = None

      key1 = "{}_{}".format(unmapped_name, "Fantasy Score")
    #   key2 = "{}_{}".format(unmapped_name, "FSComputed")
      key2 = "{}_{}".format(unmapped_name, "CaesarsComputed")
      if key1 in name_stat_to_val:
          proj = name_stat_to_val[key1]

          if position == 'WR' and site == 'fd':
            proj *= 0.86


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
      if name in to_exclude:
          continue

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

def get_player_pool(slate_players, scraped_lines, site, team_filter=None, adjustments={}):
    computed_stats_to_pass = []
    # if site == 'fd':
    #     computed_stats_to_pass = computed_stats
    # else:
    #     computed_stats_to_pass = [computed_stats[1]]

    name_stat_to_val, seen_names, seen_stats = get_player_projection_data(scraped_lines, team_filter, computed_stats=computed_stats_to_pass)


    ## TODO: this is the current exclude list
    player_pool = _get_player_pool(name_stat_to_val, seen_names, slate_players, site, to_exclude=[])

    for player in player_pool:
        name = player[0]
        if name in adjustments:
            player[2] = adjustments[name] * player[2]

    return player_pool

def print_slate(slate_players, player_pool, site, teams):
    for team in teams:
        print("-----------------")
        print(team)
        print("-----------------")
        if site == 'dk' and team == 'JAC':
            team = 'JAX'
        slate_players1 = [a for a in slate_players if a['team'] == team]
        players_sorted = sorted(slate_players1, key=lambda a: int(a['salary']), reverse=True)
        rows = []
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
            
            cuttoff_salary = 2000
            # if site == 'fd':
            #     cuttoff_salary = 4500

            # if 'DST' in position:
            #     import pdb; pdb.set_trace()
            if float(salary) >= cuttoff_salary or 'DST' in position:
                rows.append([name, salary, position, projected])

        print(tabulate(rows, headers=['Name', 'Salary', 'Position', 'Projected']))

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


def get_locked_players_key(players):
  to_return = ""
  for player in players:
    if player != '':
      to_return += player.name

    to_return += "|"

  return to_return

def get_roster_keys_from_rosters(rosters):
  #  [b.name for b in [a.players for a in candidate_rosters][0]]
  roster_keys = []
  for roster in rosters:
    players = roster.players
    names = [a.name for a in players]
    roster_keys.append(",".join(sorted(names)))

  return roster_keys

def reoptimize_fd_nba(player_pool, locked_rosters, original_rosters):
    by_position = {'PG': [], 'SG': [], 'SF': [], 'PF': [], 'C': []}

    def lineup_validator(roster):
        team_ct = {}
        for player in roster.players:
            pl_team = player.team
            if not pl_team in team_ct:
                team_ct[pl_team] = 1
            else:
                team_ct[pl_team] += 1
        return max(team_ct.values()) <= 4

    for player in player_pool:
        name = player[0]
        cost = player[1]
        proj = player[2]
        position = player[3]
        team = player[4]
        pos_parts = position.split('/')
        for pos in pos_parts:
            player = utils.Player(name, player, cost, team, proj)
            by_position[pos].append(player)

    print(by_position)

    optimizer = FD_NBA_Optimizer()
    all_results = []

    seen_roster_strings = []
    seen_roster_string_to_optimized_roster = {}
    roster_idx = 0
    locked_players_to_top_n_optimized = {}
    seen_roster_keys = []
    is_se_roster_or_h2h = False

    for players in locked_rosters:
        lock_ct = sum([1 for a in players if a is not ''])
        if lock_ct != 9:
            locked_players_key = get_locked_players_key(players)

            if not locked_players_key in locked_players_to_top_n_optimized:
                candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(12950), players, lineup_validator=lineup_validator)
                # TODO: 6050
                # candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(11050), players5, is_roster_valid)

                candidate_rosters_keys = get_roster_keys_from_rosters(candidate_rosters)
                # TODO: consider filtering out currently in-play rosters from these candidates to avoid collisions?

                locked_players_to_top_n_optimized[locked_players_key] = candidate_rosters
            else:
                candidate_rosters = locked_players_to_top_n_optimized[locked_players_key]   
                    # result = optimizer.optimize(by_position, players, int(2500), lineup_validator=lineup_validator)
                    # result = optimizer.optimize(by_position, players, int(5000), lineup_validator=lineup_validator)

            top_roster = candidate_rosters[0]
            top_val = top_roster.value
            candidate_rosters_filtered = [a for a in candidate_rosters if a.value >= top_val - 10]
            if not is_se_roster_or_h2h:
                counter = 0
                for roster in candidate_rosters_filtered:
                    names1 = [p.name for p in roster.players]
                    candidate_roster_key = ",".join(sorted(names1))
                    if not candidate_roster_key in seen_roster_keys:
                        result = roster
                        print("TAKING CANDIDATE ROSTER: {}".format(counter))
                        break

                    counter += 1
                
                names1 = [p.name for p in result.players]
                optimized_roster_key = ",".join(sorted(names1))
                seen_roster_keys.append(optimized_roster_key)
            else:
                result = None

        else:
            result = None
        all_results.append(result)
        print("{}/{}".format(len(all_results), len(locked_rosters)))
    
    return all_results


def optimize_fd_nba(player_pool, ct, iterCount):
    by_position = {'PG': [], 'SG': [], 'SF': [], 'PF': [], 'C': []}

    for player in player_pool:
        name = player[0]
        cost = player[1]
        proj = player[2]
        position = player[3]
        team = player[4]
        pos_parts = position.split('/')
        for pos in pos_parts:
            player = utils.Player(name, player, cost, team, proj)
            by_position[pos].append(player)

    print(by_position)

    optimizer = FD_NBA_Optimizer()

    def lineup_validator(roster):
        team_to_count = {}
        for player in roster.players:
            if not player.team in team_to_count:
                team_to_count[player.team] = 1
            else:
                team_to_count[player.team] += 1

        for team, ct in team_to_count.items():
            if ct > 4:
                return False
        return True


    # optimizer.optimize(by_position, None, 100000)
    results = optimizer.optimize_top_n(by_position, ct, iterCount * 10000, locked_players=None, lineup_validator=lineup_validator)
    return results



def optimize_dk_nba(player_pool, ct, iterCount, excluded):
    dk_positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

    by_position = {'PG': [], 'SG': [], 'SF': [], 'PF': [], 'C': [], "G": [], "F": [], "UTIL": []}

    for player in player_pool:
        name = player[0]
        if name in excluded:
            continue

        cost = player[1]
        proj = player[2]
        position = player[3]
        team = player[4]
        pos_parts = position.split('/')
        for pos in pos_parts:
            eligible_positions = dk_positions_mapper[pos]
            for eligible_position in eligible_positions:
                player = utils.Player(name, player, cost, team, proj)
                by_position[eligible_position].append(player)

    print(by_position)

    name_to_positions = {}
    for pos, players in by_position.items():
        for player in players:
            name = player.name
            if not name in name_to_positions:
                name_to_positions[name] = []
            name_to_positions[name].append(pos)

    optimizer = DK_NBA_Optimizer()

    results = optimizer.optimize_top_n(by_position, ct, locked_players=None, iter=iterCount * 10000)
    return results, name_to_positions


dk_positions = ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"]

def consider_swap(idx1, idx2, team_to_start_time, players, name_to_positions, locked_players):
    if locked_players != None and (locked_players[idx1] != '' or locked_players[idx2] != ''):
        return
    # if one of these players is locked (zero projection) abort the swap
    player1 = players[idx1]
    player2 = players[idx2]
    # player 1 is specific
    # player 1 is general
    # we want specific to be before the general
    team1 = player1.team
    team2 = player2.team

    team1 = utils.normalize_team_name(team1)
    team2 = utils.normalize_team_name(team2)

    if team_to_start_time[team1] > team_to_start_time[team2]:
        # make sure the swap is valid!
        positions = name_to_positions[player2.name]
        if any([p == dk_positions[idx1] for p in positions]):
            # execute swap
            players[idx2] = player1
            players[idx1] = player2

def optimize_dk_roster_for_late_swap(roster, start_times, name_to_positions, locked_players = None):
    team_to_start_time = {}
    for time, teams in start_times.items():
        for team in teams:
            team_to_start_time[team] = time

    players = roster.players

    consider_swap(0, 5, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(1, 5, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(2, 6, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(3, 6, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(0, 7, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(1, 7, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(2, 7, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(3, 7, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(4, 7, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(5, 7, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(6, 7, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(0, 5, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(1, 5, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(2, 6, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(3, 6, team_to_start_time, players, name_to_positions, locked_players)
    consider_swap(0, 7, team_to_start_time, players, name_to_positions, locked_players)

def optimize(sport, site, slate_id, roster_count, iter_count, excluded):
    assert site == 'fd' or site == 'dk'
    print("{} NBA {}".format(site, slate_id))

    scraped_lines = data_utils.get_scraped_lines_multiple(['PrizePicks_' + sport, 'Caesars_' + sport])

    table_root = "FDSlatePlayers_"
    if site == 'dk':
        table_root = "DKSlatePlayers_"

    slate_players, team_list, name_to_id = data_utils.get_slate_players_and_teams(table_root, sport, slate_id, exclude_injured=site == 'fd')
    
    ## TODO - refactor this into a component?
    player_pool = get_player_pool(slate_players, scraped_lines, site, team_filter=None, adjustments={
    })

    print_slate(slate_players, player_pool, site, team_list)

    if site == 'fd':
        results = optimize_fd_nba(player_pool, roster_count, iter_count)
    elif site == 'dk':
        results, name_to_positions = optimize_dk_nba(player_pool, roster_count, iter_count, excluded)
        most_recent_slate = data_utils.get_most_recent_slate(sport)
        start_times = utils.parse_start_times_from_slate(most_recent_slate['slate'])
        for roster in results:
            optimize_dk_roster_for_late_swap(roster,
                                             start_times, name_to_positions)

    return results, name_to_id

def _get_player_from_slate(slate_players, name):
    for player in slate_players:
        if player['name'] == name:
            return [name, float(player['salary']), 0, player['position'], player['team']]
    
    print(name)
    import pdb; pdb.set_trace()


def reoptimize(sport, site, slate_id, rosters):
    assert site == 'fd'
    print("Reoptimize FD NBA", slate_id)

    scraped_lines = data_utils.get_scraped_lines_multiple(['PrizePicks_' + sport, 'Caesars_' + sport])

    slate_players, team_list, name_to_id = data_utils.get_slate_players_and_teams("FDSlatePlayers_", sport, slate_id, site == 'fd')


    player_pool = get_player_pool(slate_players, scraped_lines, 'fd', team_filter=None, adjustments={
    })
    
    most_recent_slate = data_utils.get_most_recent_slate(sport)

    start_times = utils.parse_start_times_from_slate(most_recent_slate['slate'])
    print(start_times)

    now = datetime.datetime.now()
    current_time = (now.hour - 12) + (now.minute / 60)
    current_time = round(current_time, 2)

    # current_time = 8.6
    print("CURRENT TIME: {}".format(current_time))

    locked_teams = []
    for key, value in start_times.items():
        if key < current_time:
            locked_teams += value

    print(locked_teams)

    locked_rosters = []
    original_rosters = []
    lines = rosters.split('\n')
    for line in lines:
        players = line.split('	')
        locked_roster_players = []
        original_roster_players = []
        for player in players:
            name = player.split(':')[1]
            matched_players = [a for a in player_pool if a[0] == name]
            if len(matched_players) == 0:
                matched_player = _get_player_from_slate(slate_players, name)
            elif len(matched_players) > 1:
                print("Error", name)
                import pdb; pdb.set_trace()
                assert False
            else:
                matched_player = matched_players[0]
            name = matched_player[0]
            cost = matched_player[1]
            proj = matched_player[2]
            team = matched_player[4]
            player_new = utils.Player(name, '', cost, team, proj)
            original_roster_players.append(player_new.clone())
            if team in locked_teams:
                locked_roster_players.append(player_new)
            else:
                locked_roster_players.append('')
            
        locked_rosters.append(locked_roster_players)
        original_rosters.append(utils.Roster(original_roster_players))
    
    player_pool_new = [a for a in player_pool if a[4] not in locked_teams]
    
    if sport == 'NFL':
        results = reoptimize_fd_nfl(player_pool_new, 8, locked_rosters)
    elif sport == 'NBA':
        results = reoptimize_fd_nba(player_pool_new, locked_rosters, original_rosters)


    name_to_id = utils.name_to_player_id(slate_players)

    return results, original_rosters, name_to_id