from tinydb import TinyDB, Query, where
import itertools
import requests
import json
import time
import boto3



import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')

from optimizer_library import NFL_Optimizer
import optimizer
import utils
import os
from name_mapper import dk_name_to_fd_name
import data_utils



# open fd slate file and dk slate file
# parse relevant columns
#name, normalized name, pos, salary, team

# generate name (fd, dk) -> id
# id -> projection, status
# team -> start time, opp
# slates -> teams, slate name1


aws_access_key_id = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

s3 = boto3.client('s3',
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key,
                  region_name='us-east-1')

def write_file(content, name):
    bucket_name = 'amichai-dfs-data'  # S3 bucket name
    s3.put_object(Body=content, Bucket=bucket_name, Key=name)

date = '2023-11-22'

# we should actually pull this from the `current` table on any given day
lines = data_utils.get_scraped_lines_for_date('Caesars', date)
name_to_projection = data_utils.scraped_lines_to_projections(lines, 'fd')

name_to_projection_2 = {}
for name, proj in name_to_projection.items():
    name_madded = name
    if name in dk_name_to_fd_name:
        name_madded = dk_name_to_fd_name[name]
    name_to_projection_2[name_madded] = proj

path = './DBs/NBA/slates_' + date + '.txt'

fd_names = {}

# to upload
# [slate id, player name, player id, pos, salary]
slate_player_data = ''
# [name, team, projection, status]
player_data = ''
# [team, start_time, opp]
team_data = ''
#[slate id, slate name, start_time, end_time, site]
slate_data = ''



# seen_names = []
# seen_matchups = []
# team_to_start_time = {}

# file = open(path, 'r')
# lines = file.readlines()
# site = None
# for line in lines:
#     line = line.strip()
#     if 'game data:' in line:
#         game_data = line.replace('game data: ', '').strip().replace(',', '\n')
#         start_times = utils.parse_start_times_from_slate(game_data)
#         for t, teams in start_times.items():
#             for team in teams:
#                 team_to_start_time[team] = t
#         continue
    
#     if 'columns:' in line:
#         continue
#     if 'site: fd' in line:
#         site = 'fd'
#         continue
#     elif 'site: dk' in line:
#         site = 'dk'
#         continue
    
#     if site == 'dk':
#         continue
    
#     assert site is not None
    
#     parts = line.split(',')
#     assert len(parts) == 7, line
    
#     id = parts[0]
    
#     name = parts[2]
#     position = parts[1]
#     salary = parts[3]
#     matchup = parts[4]
#     team = parts[5]
#     status = parts[6]
    
#     projection = str(name_to_projection_2.get(name, None))
        
        
#     all_slate_lines += ",".join([id, name, position, salary]) + '\n'
#     if not name in seen_names:
#         player_data += ','.join([name, team, projection, status]) + '\n'
#         seen_names.append(name)
        
#     if not matchup in seen_matchups:
#         team_data += ','.join([matchup, str(team_to_start_time[team])]) + '\n'
#         seen_matchups.append(matchup)
    
    
write_file(slate_player_data, 'slate_player_data')
write_file(team_data, 'team_data')
write_file(player_data, 'player_data')
write_file(slate_data, 'slate_data')