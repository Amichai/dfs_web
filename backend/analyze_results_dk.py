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

id_to_name = {}
name_to_id = {}

f = open('dataset3.json', 'r')
as_json = json.loads(f.read())
for player in as_json:
  name_full = player['name']
  points = player['points']
  if points == None:
    points = '0'
  id = player['site_id']
  name_parts = name_full.split(' : ')
  if name_parts[1] == 'CPT':
    continue
  
  name = name_parts[0]
  id_to_name[id] = name
  name_to_points[name] = points
  name_to_id[name] = id
  name_to_points[name] = points
  
csv_files = {
  '100%': 'DK SHOWDOWN_ (BOS vs DEN) 10_00pm ET 150 entries.csv',
  '60%': 'DK SHOWDOWN_ (BOS vs DEN) 10_00pm ET 150 entries (1).csv',
  # '100%': 'DK SHOWDOWN_ (TOR vs PHX) 09_00pm ET 150 entries.csv',
  # '50%': 'DK SHOWDOWN_ (TOR vs PHX) 09_00pm ET 150 entries (1).csv',
  # '100%': 'DK SHOWDOWN_ (MIA vs DAL) 07_30pm ET 150 entries.csv',
  # '80%': 'DK SHOWDOWN_ (MIA vs DAL) 07_30pm ET 150 entries (2).csv',
  # '50%': 'DK SHOWDOWN_ (MIA vs DAL) 07_30pm ET 150 entries (1).csv',
  # '80%': 'min vs ind 150 entries.csv',
  # '70%': 'DK SHOWDOWN_ (MIN vs IND) 07_00pm ET 150 entries (3).csv',
  # '60%': 'DK SHOWDOWN_ (MIN vs IND) 07_00pm ET 150 entries (4).csv',
  # '50%': 'DK SHOWDOWN_ (MIN vs IND) 07_00pm ET 150 entries (5).csv',
}

site_to_entry_ids = {}
entry_id_to_names = {}

for site, path in csv_files.items():
  site_to_entry_ids[site] = []
  path = download_folder + path
  row_counter = 0
  with open(path, 'r') as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
      entry_id = row[0]
      if entry_id == '' or entry_id == 'Entry ID':
        continue
      
      entry_id = str(row_counter) + '_' + site
      row_counter += 1
      site_to_entry_ids[site].append(entry_id)
      player_names = []
      for i in range(6):
        player_id = row[4 + i]
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
  first_player = True
  for player_name in player_names:
    if player_name not in name_to_points:
      print(f'player name {player_name} not found')
      import pdb; pdb.set_trace()
      
    pts = name_to_points[player_name]
    if first_player:
      roster_sum += float(pts) * 1.5
      first_player = False
    else:
      roster_sum += float(pts)
    
    
  entry_id_to_score[entry_id] = round(roster_sum, 2)
  
  
def evaluate_scores(scores):
  mx = max(scores)
  mn = min(scores)
  av = round(statistics.mean(scores), 2)
  md = statistics.median(scores)
  max_idx = scores.index(mx)
  sorted_scores = sorted(scores, reverse=True)[:10]
  print(f'max: {mx}, min: {mn} average: {av}, median: {md}, max idx: {max_idx}')
  print(scores[:10])

seen_names = []
site_to_player_exposure = {}
total_sum = 0
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
      total_sum += 1
      
  site_to_player_exposure[site] = name_to_ct


sites = list(site_to_player_exposure.keys())
table = []
for name in seen_names:
  for site in sites:
    if name not in site_to_player_exposure[site]:
      site_to_player_exposure[site][name] = 0
  # table.append([name, site_to_player_exposure[sites[0]][name],
  #               site_to_player_exposure[sites[1]][name],
  #               site_to_player_exposure[sites[2]][name]])
  to_append = [name]
  to_append.extend([site_to_player_exposure[site][name] for site in sites])
  table.append(to_append)
  

table_sorted = sorted(table, key=lambda a: a[1], reverse=True)
headers = ['Name']
headers.extend(sites)
print(tabulate(table_sorted, headers=headers))

site_to_scores = {}
for site, entry_ids in site_to_entry_ids.items():
  site_to_scores[site] = []
  for entry_id in entry_ids:
    site_to_scores[site].append(entry_id_to_score[entry_id])
    
  print(site)
  evaluate_scores(site_to_scores[site])
