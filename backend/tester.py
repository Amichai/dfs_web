from tinydb import TinyDB, Query, where
import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
import utils
import optimizer

import numpy as np
from geneticalgorithm import geneticalgorithm as ga

algorithm_param = {'max_num_iteration': 50000,
                   'population_size': 20,
                   'mutation_probability': 0.05,
                   'elit_ratio': 0.01,
                   'crossover_probability': 0.9,
                   'parents_portion': 0.3,
                   'crossover_type': 'two_point',
                   'max_iteration_without_improv': 10000}

DB_ROOT = 'DBs/'
SCRAPE_OPERATIONS_TABLE = 'scrape_operations'

def _get_scraped_lines(scraper):
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

def test_optimizer1(sport, slate_id):
  print("FD NFL", slate_id)
  db = TinyDB(DB_ROOT + "FDSlatePlayers_" + sport)
  scraped_lines = _get_scraped_lines('PrizePicks_' + sport)

  query = Query()
  slate_players = db.search((query['slateId'] == slate_id))

  player_pool = optimizer.get_player_pool(slate_players, scraped_lines, 'fd')

  name_to_id = utils.name_to_player_id(slate_players)
  name_to_id = utils.map_pp_defense_to_fd_defense_name(name_to_id)
  results = optimizer.optimize_fd_nfl(player_pool, 10)

  for result in results:
      to_print = ["{}:{}".format(name_to_id[a.name], a.name) for a in result.players]
      print(",".join(to_print) + "," + str(result.value))

def test_optimizer2(sport, slate_id):
  print("FD NFL", slate_id)
  db = TinyDB(DB_ROOT + "FDSlatePlayers_" + sport)
  scraped_lines = _get_scraped_lines('PrizePicks_' + sport)

  query = Query()
  slate_players = db.search((query['slateId'] == slate_id))

  player_pool = optimizer.get_player_pool(slate_players, scraped_lines, 'fd')
  print(player_pool)


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




  name_to_id = utils.name_to_player_id(slate_players)
  name_to_id = utils.map_pp_defense_to_fd_defense_name(name_to_id)
  # results = optimizer.optimize_fd_nfl(player_pool, 10)

  roster_index_positions = ['QB', 'RB', 'RB', 'WR', 'WR', 'WR', 'TE', 'FLEX', 'D']

  top_n = []
  seen_roster_keys = []

  def f(X):
    # lookup each players
    # no duplicates
    # all positions covered
    # within salary cap
    # no more than 4 players from same team
    # maximize player value sum
    player_set = []
    player_names = []
    duplication_penalty = 0
    for i, player_index in enumerate(X):
      pos = roster_index_positions[i]
      
      player = by_position[pos][int(player_index) - 1]
      if player.name in player_names:
        duplication_penalty += 10
      else:
        player_names.append(player.name)
      player_set.append(player)


    assert len(player_set) == 9, len(player_set)
    total_cost = sum(p.cost for p in player_set)
    cost_overrun = max((total_cost - 60000), 0)
    total_value = sum(p.value for p in player_set)
    # value_penalty = sum(1.0 / p.value for p in player_set)
    value_penalty = 1.0 / total_value
    total_penalty = value_penalty + duplication_penalty + cost_overrun

    roster_key = "|".join(sorted([a.name for a in player_set])) + "|" + str(round(total_value, 2))

    if cost_overrun == 0 and duplication_penalty == 0 and roster_key not in seen_roster_keys:
      top_n.append((player_set, total_penalty, total_value, total_cost))
      seen_roster_keys.append(roster_key)


    return total_penalty

  varbound = np.array([[0,len(by_position['QB'])],[0,len(by_position['RB'])],[0,len(by_position['RB'])],[0,len(by_position['WR'])],[0,len(by_position['WR'])],[0,len(by_position['WR'])],[0,len(by_position['TE'])],[0,len(by_position['FLEX'])],[0,len(by_position['D'])]])
  vartype = np.array([['int'],['int'],['int'],['int'],['int'],['int'],['int'],['int'],['int']])

  model=ga(function=f,dimension=9,variable_type_mixed=vartype,variable_boundaries=varbound, algorithm_parameters=algorithm_param, convergence_curve=False)


  model.run()
  print('-------')



  print(len(top_n))
  rosters_sorted = sorted(top_n, key=lambda a: a[1])
  for roster in rosters_sorted[:20]:
   print("{}, {}, {}".format(roster[2], roster[1], roster[0]))


  
  print(model.output_dict)
  roster = []
  arr = model.output_dict['variable']
  for index, position in enumerate(roster_index_positions):
    player = by_position[position][int(arr[index]) - 1]
    # print(by_position[position][int(arr[index]) - 1])
    roster.append(player)







  print(roster)
  print(sum([a.value for a in roster]))
  print(sum([a.cost for a in roster]))
  # print(model.report)


  # for result in results:
  #     to_print = ["{}:{}".format(name_to_id[a.name], a.name) for a in result.players]
  #     print(",".join(to_print) + "," + str(result.value))


sport = "NFL"
slate_id = "92765"
test_optimizer1(sport, slate_id)
# test_optimizer2(sport, slate_id)



# GA:
# {'variable': array([ 7.,  4.,  2.,  0., 11., 13.,  1.,  3.,  7.]), 'function': 7.738064590701038}
# [Jalen Hurts - 23.0 - PHI, James Conner - 13.0 - ARI, Miles Sanders - 11.75 - CAR, Chris Godwin - 13.0 - TB, DeVonta Smith - 12.0 - PHI, Mike Evans - 12.5 - TB, Zach Ertz - 9.0 - ARI, Kenneth Walker III - 13.5 - SEA, Eagles DST - 7.0 - PHI]
# 114.75
# 59800.0