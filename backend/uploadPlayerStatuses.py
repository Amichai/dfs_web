import csv
import scripts_util

import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
from name_mapper import dk_name_to_fd_name

excluded_players = scripts_util.read_file('player_statuses').split('\n')

excluded_players = [a for a in excluded_players if a != '']

excluded_players_dict = {a.split(',')[0]: a.split(',') for a in excluded_players}

fd_name_to_dk_name = {v: k for k, v in dk_name_to_fd_name.items()}

download_folder = '/Users/amichailevy/Downloads/'
filenames = [
  'FanDuel-NBA-2024 ET-03 ET-19 ET-100511-players-list (1).csv',
]
exclude = []

new_statuses = []
updated_statuses = []

for file in filenames:
  path = download_folder + file
  with open(path, 'r') as f:
    reader = csv.reader(f, delimiter=',', quotechar='"')
    for row in reader:
        if row[0] == 'Id' or row[0] == 'Position':
            continue
        
        name = row[3]
        names = [name]
        if name in fd_name_to_dk_name.keys():
          names += [fd_name_to_dk_name[name]]
        
        team = row[9]
        status = row[11]
        
        for name in names:
          if name in exclude:
            status = 'O'
          if status != 'O' and status != 'GTD':
            
            ### TODO: if you can find this name in the existing player statuses rows, then remove that row!
            continue
          
          if name not in excluded_players_dict.keys():
            new_statuses.append(f'{name},{status}')
            
            excluded_players_dict[name] = [name,team,'FD',status]
          else:
            excluded_players_dict[name][2] = 'FD'
            old_status = excluded_players_dict[name][3]
            excluded_players_dict[name][3] = status
            if old_status != status:
              updated_statuses.append(f'{name},{old_status} -> {status}')
          

rows = [','.join(a) for a in excluded_players_dict.values()]
scripts_util.write_file('\n'.join(rows), 'player_statuses')
print("new statuses:")
for status in new_statuses:
  print(status)
  
print("updated statuses:")
for status in updated_statuses:
  print(status)
  
  