import csv
import json
import statistics
from tabulate import tabulate

# open my 3 csv files
# get the lineups for each file
# compute actual scores
# sort by highest score, highest average score, etc
# biggest exposure differences
download_folder = '/Users/amichailevy/Downloads/'
name_to_points = {}

# f = open('dataset.json', 'r')
with open(download_folder + 'NBA_2024-02-29-700pm_FD_Main.csv', 'r') as f:
  reader = csv.reader(f, delimiter=',', quotechar='"')
  reader = csv.reader(f, delimiter=',', quotechar='"')
  for row in reader:
    if row[0] == 'DFS ID':
      continue
    name = row[1]
    score = row[7]
    name_to_points[name] = score
    

# import pdb; pdb.set_trace()
    
    
# result = f.read()
# as_json = json.loads(result)

# for player in as_json:
#   name = player['name']
#   points = player['points']
#   name_to_points[name] = points

player_list_path = 'FanDuel-NBA-2024 ET-02 ET-29 ET-99788-players-list (2).csv'

csv_files = {
  'DFS Crunch': 'dfscrunch5.csv',
  'Stokastic': 'FD Main 07_00pm ET 50 entries (2).csv',
  'Saber Sims': 'entries_fd_nba_2024-02-29_700pm_main (3).csv' 
}

id_to_name = {}
name_to_id = {}
path = download_folder + player_list_path
with open(path, 'r') as f:
  reader = csv.reader(f, delimiter=',', quotechar='"')
  for row in reader:
    if row[0] == 'Id' or row[0] == 'Position':
      continue
    player_id = row[0]
    player_name = row[3]
    id_to_name[player_id] = player_name
    name_to_id[player_name] = player_id

# in my video, report on FC/Stokastic fail. Reoptimization challenges, future plan


site_to_entry_ids = {}
entry_id_to_names = {}

for site, path in csv_files.items():
  site_to_entry_ids[site] = []
  path = download_folder + path
  with open(path, 'r') as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
      entry_id = row[0]
      if entry_id == '' or entry_id == 'entry_id':
        continue
      site_to_entry_ids[site].append(entry_id)
      player_names = []
      if row[2] == 'contest_name':
        continue
      for i in range(9):
        player_id = row[3 + i]
        if(':') in player_id:
          player_id = player_id.split(':')[0]
        if not player_id in id_to_name:
          print(f'player id {player_id} not found')
          import pdb; pdb.set_trace()
        player_name = id_to_name[player_id]
        player_names.append(player_name)
      entry_id_to_names[entry_id] = player_names


entry_id_to_score = {}

for entry_id, player_names in entry_id_to_names.items():
  roster_sum = 0
  for player_name in player_names:
    if player_name not in name_to_points:
      print(f'player name {player_name} not found')
      import pdb; pdb.set_trace()
      
    pts = name_to_points[player_name]
    roster_sum += float(pts)
    
  entry_id_to_score[entry_id] = round(roster_sum, 2)
  
  
def evaluate_scores(scores):
  mx = max(scores)
  mn = min(scores)
  av = round(statistics.mean(scores), 2)
  md = statistics.median(scores)
  sorted_scores = sorted(scores, reverse=True)[:10]
  print(f'max: {mx}, min: {mn} average: {av}, median: {md}')
  print(scores[:10])

seen_names = []
site_to_player_exposure = {}
for site, entry_ids in site_to_entry_ids.items():
  name_to_ct = {}
  for entry_id in entry_ids:
    names = entry_id_to_names[entry_id]
    for name in names:
      if name not in seen_names:
        seen_names.append(name)
        
      if name not in name_to_ct:
        name_to_ct[name] = 0
      name_to_ct[name] += 1
  site_to_player_exposure[site] = name_to_ct


sites = list(site_to_player_exposure.keys())
table = []
for name in seen_names:
  for site in sites:
    if name not in site_to_player_exposure[site]:
      site_to_player_exposure[site][name] = 0
  table.append([name, site_to_player_exposure[sites[0]][name],
                site_to_player_exposure[sites[1]][name],
                site_to_player_exposure[sites[2]][name]])

table_sorted = sorted(table, key=lambda a: a[1], reverse=True)
print(tabulate(table_sorted, headers=['Name', sites[0], sites[1], sites[2]]))

site_to_scores = {}
for site, entry_ids in site_to_entry_ids.items():
  site_to_scores[site] = []
  for entry_id in entry_ids:
    site_to_scores[site].append(entry_id_to_score[entry_id])
    
  print(site)
  evaluate_scores(site_to_scores[site])
