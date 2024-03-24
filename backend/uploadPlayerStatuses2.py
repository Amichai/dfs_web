import csv
import scripts_util
import os
import requests
import time

import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
from name_mapper import dk_name_to_fd_name
import utils

excluded_players = scripts_util.read_file('player_statuses').split('\n')

excluded_players = [a for a in excluded_players if a != '']

excluded_players_dict = {a.split(',')[0]: a.split(',') for a in excluded_players}

fd_name_to_dk_name = {v: k for k, v in dk_name_to_fd_name.items()}
download_folder = '/Users/amichailevy/Downloads/'

########
contest_ids = [159886990, 159873777]
exclude = []
########

draftGroups = ['103070', '103311']

if len(draftGroups) == 0:
  for contest_id in contest_ids:
    result = requests.get(f'https://www.draftkings.com/draft/contest/{contest_id}')
    time.sleep(1)
    as_text = result.text
    match_idx = as_text.index('draftGroupId')
    extracted = as_text[match_idx: match_idx + 20]
    draftGroup = extracted.split(':')[1]
    draftGroups.append(draftGroup)
    
  print("Resolved draft groups: ", draftGroups)
  assert False

status_mapper = {
  'Q': 'GTD',
  'OUT': 'O',
  'None': '',
}


new_statuses = []
updated_statuses = []

for draftGroup in draftGroups:
  result = requests.get(f'https://api.draftkings.com/draftgroups/v1/draftgroups/{draftGroup}/draftables?format=json')
  time.sleep(1)
  as_json = result.json()
  for player in as_json['draftables']:
    name = player['displayName']
    names = [name]
    fd_name = None
    if name in dk_name_to_fd_name:
      names += [dk_name_to_fd_name[name]]
      

    team = player['teamAbbreviation']
    status = player['status']
    status = status_mapper[status]
    
    name_idx = 0
    for name in names:
      name_idx += 1
      
      if name in exclude:
        status = 'O'
      if status != 'O' and status != 'GTD':
        
        ### TODO: if you can find this name in the existing player statuses rows, then remove that row!
        continue
      
      if name not in excluded_players_dict.keys():
        if name_idx == 1:
          new_statuses.append((name, status))
        
        excluded_players_dict[name] = [name,team,'DK',status]
      else:
        excluded_players_dict[name][2] = 'DK'
        old_status = excluded_players_dict[name][3]
        excluded_players_dict[name][3] = status
        if old_status != status and name_idx == 1:
          updated_statuses.append((name, old_status, status))
        

append_to_news_feed = ''

rows = [','.join(a) for a in excluded_players_dict.values()]
scripts_util.write_file('\n'.join(rows), 'player_statuses')
print("new statuses:")
for name, status in new_statuses:
  print(f'{name} -> {status}')
  if status == 'O':
    append_to_news_feed += f'{name} marked OUT\n'
  
print("updated statuses:")
for name, oldStatus, newStatus in updated_statuses:
  print(f'{name} {oldStatus} -> {newStatus}')
  if newStatus == 'O':
    append_to_news_feed += f'{name} marked OUT\n'
  

if len(append_to_news_feed) > 0:
  date_suffix = utils.date_str()
  news_feed_file_name = 'news_feed_{}'.format(date_suffix)
  current_news_feed = scripts_util.read_file(news_feed_file_name)
  news_feed_string = "{}{}".format(current_news_feed, append_to_news_feed) ##append to news feed has the trailing newline
  scripts_util.write_file(news_feed_string, news_feed_file_name)
  
  