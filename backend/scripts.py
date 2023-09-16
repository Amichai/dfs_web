from tinydb import TinyDB, Query, where
import itertools

import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')

from optimizer_library import NFL_Optimizer
import utils


from app import _get_scraped_lines

DB_ROOT = 'DBs/'

SCRAPE_OPERATIONS_TABLE = 'scrape_operations'


# slate_lines_dk = _get_slate_data('DKSlatePlayers_NFL', '89943,89970')
# player_pool = get_player_pool(name_stat_to_val, seen_names, slate_lines_dk)
# print("DK: ", player_pool)
# optimize_for_single_game_dk(player_pool, 5)


# slate_lines_fd = _get_slate_data('FDSlatePlayers_NFL', '92765')
# player_pool = get_player_pool(name_stat_to_val, seen_names, slate_lines_fd)
# print("FD: ", player_pool)
# # optimize_for_single_game_fd(player_pool, 5)

# by_position = {'QB': [], 'RB': [], 'WR': [], 'TE': [], 'FLEX': [], 'D': []}

# for player in player_pool:
#    name = player[0]
#    cost = player[1]
#    proj = player[2]
#    position = player[3]
#    team = player[4]
#    player = utils.Player(name, player, cost, team, proj)

#    by_position[position].append(player)
#    if position != 'D' and position != 'QB':
#     by_position['FLEX'].append(player)


# print(by_position)

# optimizer = NFL_Optimizer()
# # optimizer.optimize(by_position, None, 100000)
# results = optimizer.optimize_top_n(by_position, 16, 100000)

# for result in results:
#    print(result)


# check the prizepicks_nfl line changes
# surface those line changes to the frontend 

##########


# # filter out any expired lines? 

# all_results = db2.search(query2['time'] == most_recent_scrape['scrape_time'])



scraper = 'PrizePicks_NFL'
target_name = 'Kirk Cousins'

query = Query()
db = TinyDB(DB_ROOT + scraper)
lines = db.search(query['name'] == target_name)

# lines = _get_scraped_lines(scraper)
for line in lines:
    if line['stat'] != 'Pass Yards':
        continue
    print(line)