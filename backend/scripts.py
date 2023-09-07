
from tinydb import TinyDB, Query, where

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

    # filter out any expired lines? 

    all_results = db2.search(query2['time'] == most_recent_scrape['scrape_time'])

    return all_results

# read all PP scraped players playing for KC or DET
# produce a CSV of all available projections

# pass yards, rush yards, receiving yards, receptions, etc.

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
    if team not in ['KC', 'DET']:
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

stat_combo = ['Pass Yards', 'Pass+Rush+Rec TDs', 'Rush Yards']

computed_stats = [
    {
      'name': 'FSComputed',
      'stats': ['Pass Yards', 'Pass TDs', 'Rush Yards'],
      'weights': [0.04, 4, 0.1]
    },
    {
      'name': 'FSComputed',
      'stats': ['Pass Yards', 'Pass+Rush+Rec TDs', 'Rush Yards'],
      'weights': [0.04, 4, 0.1]
    },
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


