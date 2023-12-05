from name_mapper import name_mapper_pp_to_fd_dk, name_mapper_pp_to_fd, name_mapper, name_mapper_pp_to_dk
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


def _get_player_pool(name_stat_to_val, seen_names, slate_lines, site, to_exclude):
  player_pool = []

  data_utils.add_casesar_projections(name_stat_to_val, seen_names, site)

  for name in seen_names:
      unmapped_name = name
      if name in name_mapper_pp_to_fd_dk:
          name = name_mapper_pp_to_fd_dk[name]
    
      elif site == 'fd' and name in name_mapper_pp_to_fd:
          name = name_mapper_pp_to_fd[name]

      elif site == 'dk' and name in name_mapper_pp_to_dk:
          name = name_mapper_pp_to_dk[name]

      if 'DST' in name:
          parsed_name = name.split(' ')[0]
          matched_names = [a for a in slate_lines if parsed_name in a['name']]
      else:
          matched_names = [a for a in slate_lines if a['name'] == name]

        
      if len(matched_names) == 0:
        #   if not '+' in name:
            # print("Can't find target to apply projection for (excluded or injured?): ", name)
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
    #   key2 = "{}_{}".format(unmapped_name, "FSComputed")
      key2 = "{}_{}".format(unmapped_name, "CaesarsComputed")
      if key1 in name_stat_to_val:
          proj = float(name_stat_to_val[key1])

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

def get_player_projection_data(scraped_lines, teams_to_include):
    seen_names = []
    seen_stats = []

    name_to_stats = {}
    name_stat_to_val = {}

    for result in scraped_lines:
        name = result['name'].strip()
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
        
    return to_return


def optimize_FIBA_dk(slate_players, scraped_lines):
    dk_positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

    by_position = {}
    for slate_player in slate_players:
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

    return results


def get_player_pool(slate_players, scraped_lines, site, team_filter=None, adjustments={}):
    name_stat_to_val, seen_names, seen_stats = get_player_projection_data(scraped_lines, team_filter)


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

def reoptimize_dk_nba(player_pool, locked_rosters, original_rosters, excluded=[]):
    by_position = utils.player_pool_to_by_position_dk_nba(player_pool, excluded)

    optimizer = DK_NBA_Optimizer()
    all_results = []

    seen_roster_strings = []
    seen_roster_string_to_optimized_roster = {}
    roster_idx = 0
    locked_players_to_top_n_optimized = {}
    seen_roster_keys = []
    is_se_roster_or_h2h = False

    for players in locked_rosters:
        lock_ct = sum([1 for a in players if a != ''])
        if lock_ct != 9:
            locked_players_key = get_locked_players_key(players)

            if not locked_players_key in locked_players_to_top_n_optimized:
                candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(11550), players)
                # candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(9250), players)

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


def add_roster_to_set(roster, roster_set):
    all_keys = [a.roster_key() for a in roster_set]
    roster_key = roster.roster_key()
    if not roster_key in all_keys:
        roster_set.append(roster)
        
    return sorted(roster_set, key=lambda a: a.value, reverse=True)

def reoptimize_nba_v2(player_pool, locked_rosters, original_rosters, by_position, optimizer, lineup_validator):
    locked_players_to_top_n_optimized = {}
    seen_roster_keys = []
    is_h2h = False
    
    player_to_value = {}
    for player in player_pool:
        player_to_value[player[0]] = player[2]
    
    total_roster_diff = 0
    all_results = []
    idx = 0
    for locked_players in locked_rosters:
        # TODO get the current roster value to compare with the new optimized roster value
        original_roster = original_rosters[idx]
        original_roster_val = sum([player_to_value[a.name] for a in original_roster.players if a.name in player_to_value])
        # import pdb; pdb.set_trace()
        
        idx += 1
        lock_ct = sum([1 for a in locked_players if a != ''])
        if lock_ct == 9:
            all_results.append(None)
            continue
        locked_players_key = get_locked_players_key(locked_players)
        if locked_players_key in locked_players_to_top_n_optimized:
            candidate_rosters = locked_players_to_top_n_optimized[locked_players_key]
        else:
            candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(29950), locked_players, lineup_validator=lineup_validator)
            
        candidate_rosters = add_roster_to_set(original_roster, candidate_rosters)
            
        locked_players_to_top_n_optimized[locked_players_key] = candidate_rosters
        top_roster = candidate_rosters[0]
        top_val = top_roster.value
        if is_h2h:
            all_results.append(top_roster)
            continue
        candidate_rosters_filtered = [a for a in candidate_rosters if a.value >= top_val - 10]
        counter = 0
        for roster in candidate_rosters_filtered:
            candidate_roster_key = roster.roster_key()
            if not candidate_roster_key in seen_roster_keys:
                result = roster
                print("TAKING CANDIDATE ROSTER: {}".format(counter))
                break

            counter += 1
        
        optimized_roster_key = result.roster_key()
        seen_roster_keys.append(optimized_roster_key)
        
        new_roster_val = sum([player_to_value[a.name] for a in result.players if a.name in player_to_value])
        all_results.append(result)
        roster_val_diff = new_roster_val - original_roster_val
        # if roster_val_diff < 0:
        #     import pdb; pdb.set_trace()
        print("Roster val diff: {}".format(round(roster_val_diff, 4)))
        total_roster_diff += roster_val_diff
        print("{}/{}".format(len(all_results), len(locked_rosters)))
        
    diff_count = 0
    for idx in range(len(original_rosters)):
        new_roster = all_results[idx]
        if new_roster == None:
            continue
        new_roster_key = new_roster.roster_key()
        roster = original_rosters[idx]
        roster_key = roster.roster_key()
        if new_roster_key != roster_key:
            diff_count += 1

    all_results_filtered = [a for a in all_results if a != None]
    if len(all_results_filtered) != len(set([a.roster_key() for a in all_results_filtered])):
        print("DUPLICATE ROSTERS FOUND")
        import pdb; pdb.set_trace()
            
    print("{} / {} rosters changed".format(diff_count, len(original_rosters)))
    print("Total roster diff: {}".format(round(total_roster_diff, 4)))
    return all_results
        
        
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

    # print(by_position)

    optimizer = FD_NBA_Optimizer()
    all_results = []

    seen_roster_strings = []
    seen_roster_string_to_optimized_roster = {}
    roster_idx = 0
    locked_players_to_top_n_optimized = {}
    seen_roster_keys = []
    is_se_roster_or_h2h = False

    for players in locked_rosters:
        lock_ct = sum([1 for a in players if a != ''])
        if lock_ct != 9:
            locked_players_key = get_locked_players_key(players)

            if not locked_players_key in locked_players_to_top_n_optimized:
                # candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(12950), players, lineup_validator=lineup_validator)
                candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(11950), players, lineup_validator=lineup_validator)
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


    diff_count = 0
    for idx in range(len(original_rosters)):
        new_roster = all_results[idx]
        if new_roster == None:
            continue
        new_roster_key = new_roster.roster_key()
        roster = original_rosters[idx]
        roster_key = roster.roster_key()
        if new_roster_key != roster_key:
            diff_count += 1

        pass
    
    print("{} / {} rosters changed".format(diff_count, len(original_rosters)))
    return all_results


def optimize_fd_nba(player_pool, ct, iterCount, excluded=[]):
    by_position = {'PG': [], 'SG': [], 'SF': [], 'PF': [], 'C': []}

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
            player = utils.Player(name, player, cost, team, proj)
            by_position[pos].append(player)


    # print(by_position)

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



def optimize_dk_nba(player_pool, ct, iterCount, excluded=[]):
    by_position = utils.player_pool_to_by_position_dk_nba(player_pool, excluded)
    # print(by_position)

    name_to_positions = {}
    for pos, players in by_position.items():
        for player in players:
            name = player.name
            if not name in name_to_positions:
                name_to_positions[name] = []
            name_to_positions[name].append(pos)

    optimizer = DK_NBA_Optimizer()

    results = optimizer.optimize_top_n(by_position, ct, iter=iterCount * 10000, locked_players=None, lineup_validator=utils.lineup_validator_dk)
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

def optimize_showdown_dk(slate_id, roster_count, excluded):
    scraped_lines = data_utils.get_scraped_lines_multiple(['Caesars_NBA'])
    
    site = 'dk'
    sport = 'NBA'
    
    slate_players, team_list, name_to_id = data_utils.get_slate_players_and_teams(site, sport, slate_id, exclude_injured=False)
    
    name_to_player = {}
    for player in slate_players:
        name = player['name']
        if not name in name_to_player:
            name_to_player[name] = player
        else:
            player1 = name_to_player[name]
            if int(player['salary']) < int(player1['salary']):
                name_to_player[name] = player
    
    slate_players_new = name_to_player.values()
    
    adjustments = {}
    for exclude in excluded:
        adjustments[exclude] = 0
        
    player_pool = get_player_pool(slate_players_new, scraped_lines, site, team_filter=None, adjustments=adjustments)
    
    print_slate(slate_players_new, player_pool, site, team_list)
    

    all_rosters = []

    roster_keys = set()

    player_pool = [a for a in player_pool if a[2] > 10.0]
    
    player_pool = [utils.Player(a[0], a[3], a[1], a[4], a[2]) for a in player_pool]
    print("Player pool ct: {}".format(len(player_pool)))
    # import pdb; pdb.set_trace()
    idx = 0
    for player in player_pool:
        p1 = player
        player_pool_new = [p for p in player_pool if p != p1]
        candidates = itertools.permutations(player_pool_new, 5)
        for candidate in candidates:
            p2 = candidate[0]
            p3 = candidate[1]
            p4 = candidate[2]
            p5 = candidate[3]
            p6 = candidate[4]

            idx += 1
            
            if idx % 1000000 == 0:
                print(idx)

            all_players = [p1, p2, p3, p4, p5, p6]
            
            total_cost = p1.cost * 1.5 + p2.cost + p3.cost + p4.cost + p5.cost + p6.cost
            if total_cost > 50000:
                continue
            
            seen_teams = []
            for p in all_players:
                team = p.team
                if not team in seen_teams:
                    seen_teams.append(team)

            if len(seen_teams) == 1:
                continue

            total_value = p1.value * 1.5 + p2.value + p3.value + p4.value + p5.value + p6.value

            roster_key = "|".join(sorted([a.name for a in candidate])) + "|" + str(round(total_value, 5))
            if roster_key in roster_keys:
                continue

            roster_keys.add(roster_key)
            # import pdb; pdb.set_trace()
            all_rosters.append(utils.RosterSingleGame([p1, p2, p3, p4, p5, p6], total_value, total_cost))

    all_rosters_sorted = sorted(all_rosters, key=lambda a: a.value, reverse=True)
    
    to_return = all_rosters_sorted[:roster_count]
        
    return to_return, name_to_id


def optimize_single_game_fd(slate_id, roster_count, excluded):
    scraped_lines = data_utils.get_scraped_lines_multiple(['Caesars_NBA'])
    
    site = 'fd'
    sport = 'NBA'
    
    slate_players, team_list, name_to_id = data_utils.get_slate_players_and_teams(site, sport, slate_id, exclude_injured=False)
    
    name_to_player = {}
    for player in slate_players:
        name = player['name']
        if not name in name_to_player:
            name_to_player[name] = player
        else:
            player1 = name_to_player[name]
            if int(player['salary']) < int(player1['salary']):
                name_to_player[name] = player
    
    slate_players_new = name_to_player.values()
    
    adjustments = {}
    for exclude in excluded:
        adjustments[exclude] = 0
        
    player_pool = get_player_pool(slate_players_new, scraped_lines, site, team_filter=None, adjustments=adjustments)
    
    print_slate(slate_players_new, player_pool, site, team_list)
    

    all_rosters = []

    roster_keys = set()

    player_pool = [a for a in player_pool if a[2] > 10.0]
    
    player_pool = [utils.Player(a[0], a[3], a[1], a[4], a[2]) for a in player_pool]
    print("Player pool ct: {}".format(len(player_pool)))
    idx = 0
    candidates = itertools.permutations(player_pool, 5)
    for candidate in candidates:
        p1 = candidate[0]
        p2 = candidate[1]
        p3 = candidate[2]
        p4 = candidate[3]
        p5 = candidate[4]

        idx += 1
        
        if idx % 1000000 == 0:
            print(idx)

        all_players = [p1, p2, p3, p4, p5]
        
        total_cost = p1.cost + p2.cost + p3.cost + p4.cost + p5.cost
        if total_cost > 60000:
            continue
        
        seen_teams = []
        for p in all_players:
            team = p.team
            if not team in seen_teams:
                seen_teams.append(team)

        if len(seen_teams) == 1:
            continue

        total_value = p1.value * 2.0 + p2.value * 1.5 + p3.value * 1.2 + p4.value + p5.value

        roster_key = "{}|{}|{}|".format(p1.name, p2.name, p3.name) + "|".join(sorted([p4.name, p5.name]))
        
        if roster_key in roster_keys:
            continue

        roster_keys.add(roster_key)
        # import pdb; pdb.set_trace()
        all_rosters.append(utils.RosterSingleGame([p1, p2, p3, p4, p5], total_value, total_cost))

    all_rosters_sorted = sorted(all_rosters, key=lambda a: a.value, reverse=True)
    
    to_return = all_rosters_sorted[:roster_count]
    for roster in to_return:
        print(roster)
        
    return to_return, name_to_id

def optimize_historical(sport, site, slate_id, roster_count, iter_count, excluded, date):
    assert site == 'fd' or site == 'dk'
    print("{} NBA {}".format(site, slate_id))

    scraped_lines = data_utils.get_scraped_lines_historical('Caesars', 'NBA', date)

    slate_players, team_list, name_to_id = data_utils.get_slate_players_and_teams(site, sport, slate_id, exclude_injured=site == 'fd', date=date)
    adjustments = {}
    for exclude in excluded:
        adjustments[exclude] = 0

    ## TODO - refactor this into a component?
    player_pool = get_player_pool(slate_players, scraped_lines, site, team_filter=None, adjustments=adjustments)

    print_slate(slate_players, player_pool, site, team_list)

    if site == 'fd':
        results = optimize_fd_nba(player_pool, roster_count, iter_count)
    elif site == 'dk':
        results, name_to_positions = optimize_dk_nba(player_pool, roster_count, iter_count)

        _, game_data = data_utils.get_slate_players(sport, site, slate_id, utils.date_str())
        start_times = utils.parse_start_times_from_slate(game_data)

        for roster in results:
            optimize_dk_roster_for_late_swap(roster,
                                             start_times, name_to_positions)

    return results, name_to_id

def optimize(sport, site, slate_id, roster_count, iter_count, excluded):
    assert site == 'fd' or site == 'dk'
    print("{} NBA {}".format(site, slate_id))

    scraped_lines = data_utils.get_scraped_lines_multiple(['Caesars_' + sport])

    slate_players, team_list, name_to_id = data_utils.get_slate_players_and_teams(site, sport, slate_id, exclude_injured=site == 'fd')
    adjustments = {}
    for exclude in excluded:
        adjustments[exclude] = 0

    ## TODO - refactor this into a component?
    player_pool = get_player_pool(slate_players, scraped_lines, site, team_filter=None, adjustments=adjustments)

    print_slate(slate_players, player_pool, site, team_list)

    if site == 'fd':
        results = optimize_fd_nba(player_pool, roster_count, iter_count)
    elif site == 'dk':
        results, name_to_positions = optimize_dk_nba(player_pool, roster_count, iter_count)

        _, game_data = data_utils.get_slate_players(sport, site, slate_id, utils.date_str())
        start_times = utils.parse_start_times_from_slate(game_data)

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


def reoptimize(sport, site, slate_id, rosters, excluded=None):
    assert site == 'fd' or site == 'dk'
    print("Reoptimize {} NBA - {}".format(site, slate_id))

    scraped_lines = data_utils.get_scraped_lines_multiple(['Caesars_' + sport])

    slate_players, team_list, name_to_id = data_utils.get_slate_players_and_teams(site, sport, slate_id, exclude_injured=site == 'fd')

    id_to_name = {v: k for k, v in name_to_id.items()}

    adjustments = {}
    for exclude in excluded:
        adjustments[exclude] = 0

    player_pool = get_player_pool(slate_players, scraped_lines, site, team_filter=None, adjustments=adjustments)

    _, game_data = data_utils.get_slate_players(sport, site, slate_id, utils.date_str())
    start_times = utils.parse_start_times_from_slate(game_data)
    print(start_times)

    now = datetime.datetime.now()
    current_time = (now.hour - 12) + (now.minute / 60)
    current_time = round(current_time, 2)
    
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
        players = line.split(',')
        if players[0] == 'entry_id' or players[0] == 'Entry ID':
            continue
        locked_roster_players = []
        original_roster_players = []
        if site == 'fd':
            player_columns = players[3:12]
        elif site == 'dk':
            player_columns = players[4:12]
        else:
            assert False
        for player in player_columns:
            if ':' in player:
                name = player.split(':')[1]
            else:
                name = id_to_name[player]
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

            if site == 'dk':
                team = utils.normalize_team_name(team)

            if team in locked_teams:
                locked_roster_players.append(player_new)
            else:
                locked_roster_players.append('')
            
        locked_rosters.append(locked_roster_players)
        original_rosters.append(utils.Roster(original_roster_players))
    
    player_pool_new = [a for a in player_pool if a[4] not in locked_teams]

    
    
    # if sport == 'NFL':
    #     results = reoptimize_fd_nfl(player_pool_new, 8, locked_rosters)
    # elif sport == 'NBA':
    if site == 'fd':
        optimizer = FD_NBA_Optimizer()
        by_position = utils.player_pool_to_by_position_fd_nba(player_pool_new)
        lineup_validator = utils.lineup_validator_fd
    elif site == 'dk':
        by_position = utils.player_pool_to_by_position_dk_nba(player_pool_new)
        optimizer = DK_NBA_Optimizer()
        lineup_validator=utils.lineup_validator_dk
        
    results = reoptimize_nba_v2(player_pool_new, locked_rosters, original_rosters, by_position, optimizer, lineup_validator)


    name_to_id = utils.name_to_player_id(slate_players)

    return results, original_rosters, name_to_id