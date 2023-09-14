from tinydb import TinyDB, Query, where
import itertools

import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')

from optimizer_library import NFL_Optimizer
import utils

DB_ROOT = 'DBs/'

SCRAPE_OPERATIONS_TABLE = 'scrape_operations'


def candidate_value(candidate):
    return candidate[0][2] * 1.5 + candidate[1][2] + candidate[2][2] + candidate[3][2] + candidate[4][2] + candidate[5][2]

def candidate_cost(candidate):
    return candidate[0][1] * 1.5 + candidate[1][1] + candidate[2][1] + candidate[3][1] + candidate[4][1] + candidate[5][1]

def optimize_for_single_game_fd(all_players, ct, locks=None):
    player_ct = len(all_players)
    all_rosters = []

    roster_keys = set()
    for i1 in range(player_ct):
        p1 = all_players[i1]
        if locks != None and p1[0] != locks[i1]:
            continue

        for i2 in range(player_ct):
            if i2 == i1:
                continue
            p2 = all_players[i2]

            if locks != None and p2[0] != locks[i2]:
                continue


            for i3 in range(player_ct):
                if i3 == i1 or i3 == i2:
                    continue
                
                p3 = all_players[i3]
                if locks != None and p3[0] != locks[i3]:
                    continue

                for i4 in range(player_ct):
                    if i4 == i1 or i4 == i2 or i4 == i3:
                        continue
                    
                    p4 = all_players[i4]
                    if locks != None and p4[0] != locks[i4]:
                        continue

                    for i5 in range(player_ct):
                        if i5 == i1 or i5 == i2 or i5 == i3 or i5 == i4:
                            continue
                        
                        p5 = all_players[i5]

                        if locks != None and p5[0] != locks[i5]:
                            continue
                        roster_set = [p1, p2, p3, p4, p5]
                        
                        total_cost = sum(pl[1] for pl in roster_set)
                        if total_cost > 60000 or total_cost <= 59000:
                            continue
                        
                        total_value = p1[2] * 2 + p2[2] * 1.5 +  p3[2] * 1.2 + p4[2] + p5[2]

                        # if all(x.team == roster_set[0].team for x in roster_set):
                        #     continue

                        roster_key = "|".join(sorted([a[0] for a in roster_set])) + "|" + str(round(total_value, 1))
                        if roster_key in roster_keys:
                            continue

                        roster_keys.add(roster_key)
                        all_rosters.append((roster_set, total_value, total_cost))
    all_rosters_sorted = sorted(all_rosters, key=lambda a: a[1], reverse=True)
    to_return = all_rosters_sorted[:ct]
    for roster in to_return:
        print(roster)
        
    return to_return


def optimize_for_single_game_dk(player_pool_all, ct, max_cpt_exposure=5, exlude=[]):
  player_pool = []
  seen_names = []
  for player in player_pool_all:
    if player[0] in exlude:
      continue
    # if not player.team in teams:
    #   continue
    if player[0] in seen_names:
      continue
    seen_names.append(player[0])
    player_pool.append(player)


  candidates = []

  print("size:")
  print(len(player_pool))

  for name in player_pool:
    capt = name

    names_filtered = [n for n in player_pool if n != capt]
    other_payers = itertools.combinations(names_filtered, 5)
    for sub_set in other_payers:
      candidate = [capt] + list(sub_set)

      total_cost = candidate_cost(candidate)
      if total_cost > 50000:
        continue
      candidates.append(candidate)
  
  sorted_by_value = sorted(candidates, key=lambda a: candidate_value(a), reverse=True)
  filtered_lineups = []
  capt_to_ct = {}
  for roster in sorted_by_value:
    cpt = roster[0][0]
    if not cpt in capt_to_ct:
      capt_to_ct[cpt] = 1
    else:
      capt_to_ct[cpt] += 1

    if capt_to_ct[cpt] > max_cpt_exposure:
      continue

    filtered_lineups.append(roster)
    if len(filtered_lineups) == 150:
      break


  for roster in filtered_lineups[:15]:
    print(roster, candidate_cost(roster), candidate_value(roster))

  # __import__('pdb').set_trace()


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

    # filter out any expired lines? 

    all_results = db2.search(query2['time'] == most_recent_scrape['scrape_time'])

    return all_results

# read all PP scraped players playing for KC or DET
# produce a CSV of all available projections

# pass yards, rush yards, receiving yards, receptions, etc.


def _get_slate_data(table, slate_id):
    query = Query()
    db = TinyDB(DB_ROOT + table)
    results = db.search((query['slateId'] == slate_id))
    return results

def get_projections():
  results = _get_scraped_lines('PrizePicks_NFL')

  seen_names = []
  seen_stats = []

  name_to_stats = {}
  name_stat_to_val = {}

  for result in results:
      name = result['name']
      line = result['line_score']
      team = result['team']
      stat = result['stat']
      if team in ['NYJ', 'BUF']:
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


  computed_stats = [
      # {
      #   'name': 'FSComputed',
      #   'stats': ['Pass Yards', 'Pass TDs', 'Rush Yards'],
      #   'weights': [0.04, 4, 0.1]
      # },
      # {
      #   'name': 'FSComputed',
      #   'stats': ['Pass Yards', 'Pass+Rush+Rec TDs', 'Rush Yards'],
      #   'weights': [0.04, 4, 0.1]
      # },
  ]

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

  return name_stat_to_val, seen_names, seen_stats

name_stat_to_val, seen_names, seen_stats = get_projections()

def get_player_pool(name_stat_to_val, seen_names, slate_lines):
  player_pool = []

  for name in seen_names:
      if name == "D.K. Metcalf":
          name = "DK Metcalf"

      if 'DST' in name:
          parsed_name = name.split(' ')[0]
          matched_names = [a for a in slate_lines if parsed_name in a['name']]
      else:
          matched_names = [a for a in slate_lines if a['name'] == name]

      if len(matched_names) == 0:
          print("Missing projection for: ", name)
          assert name != "D.K. Metcalf"
          continue
      

      # fantasy_score = 0
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

      key1 = "{}_{}".format(name, "Fantasy Score")
      key2 = "{}_{}".format(name, "FSComputed")
      if key1 in name_stat_to_val:
          proj = name_stat_to_val[key1]
      if key2 in name_stat_to_val:
          proj = name_stat_to_val[key2]


      if proj is None:
          continue
      
      # print("{},{},{}".format(name, salary, proj))
      # fantasy_score = 
      # get the player cost

      player_pool.append([name, salary, proj, position, team])
  return player_pool

# slate_lines_dk = _get_slate_data('DKSlatePlayers_NFL', '89943,89970')
# player_pool = get_player_pool(name_stat_to_val, seen_names, slate_lines_dk)
# print("DK: ", player_pool)
# optimize_for_single_game_dk(player_pool, 5)


slate_lines_fd = _get_slate_data('FDSlatePlayers_NFL', '92765')
player_pool = get_player_pool(name_stat_to_val, seen_names, slate_lines_fd)
print("FD: ", player_pool)
# optimize_for_single_game_fd(player_pool, 5)

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
results = optimizer.optimize_top_n(by_position, 16, 100000)

for result in results:
   print(result)

import pdb; pdb.set_trace()
# print(seen_names)
# print(seen_stats)

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


