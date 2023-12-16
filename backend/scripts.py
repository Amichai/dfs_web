from tinydb import TinyDB, Query, where
import itertools
import requests
import json
import time
import boto3
import csv


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

# date = '2023-11-22'
date = utils.date_str()

# we should actually pull this from the `current` table on any given day
lines = data_utils.get_scraped_lines_for_date('Caesars', date)
name_to_projection = data_utils.scraped_lines_to_projections(lines, 'fd')


path = './DBs/NBA/slates_' + date + '.txt'

fd_names = {}

# to upload
# [slate name, player id, player name, pos, salary]
slate_player_data = ''
# [name, team, projection, status]
player_data = ''
# [team, start_time, opp]
team_data = ''
#[slate name, site]
slate_data = ''

download_folder = '/Users/amichailevy/Downloads/'

path_and_slate_names = [
    ('FanDuel-NBA-2023 ET-12 ET-07 ET-96982-players-list.csv', 'FD Main'),
    ('DKSalaries (9).csv', 'DK Main'),
    ('DKSalaries (10).csv', 'DK NOP@LAL Showdown'),
]

seen_teams = []

for path_and_slate in path_and_slate_names:
    path = download_folder + path_and_slate[0]
    slate_name = path_and_slate[1]
    is_fd = 'FD' in slate_name
    is_dk = 'DK' in slate_name
    assert is_fd or is_dk and (is_fd != is_dk)
    
    slate_data += '{},{}\n'.format(slate_name, 'FD' if is_fd else 'DK')
    
    seen_player_ids = []

    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        for row in reader:
            if row[0] == 'Id' or row[0] == 'Position':
                continue
            if is_fd:
                ids = row[0].split('-')
                player_id = ids[1]
                positions = row[1]
                name = row[3]
                salary = row[7]
                game = row[8]
                team = row[9]
                opp = row[10]
                status = row[11]
                
                if player_id not in seen_player_ids:
                    projection = 0.0
                    if name in name_to_projection:
                        projection = name_to_projection[name]
                    else:
                        print('no projection for {} - {}'.format(name, status))
                    player_data += '{},{},{},{}\n'.format(name, team, projection, status)
                    seen_player_ids.append(player_id)
            elif is_dk:
                positions = row[0]
                name = row[2]
                if name in dk_name_to_fd_name:
                    name = dk_name_to_fd_name[name]
                player_id = row[3]
                salary = row[5]
                game_parts = row[6].split(' ')
                game = game_parts[0]
                team = row[7]
                status = ''
                
                if not team in seen_teams:
                    team_normalized = utils.normalize_team_name(team)
                    
                    teams = game.split('@')
                    opp = teams[0] if team == teams[1] else teams[1]
                    
                    opp_normalized = utils.normalize_team_name(opp)
                    team_data += '{},{},{}\n'.format(team_normalized, opp_normalized, '{} {}'.format(game_parts[-2], game_parts[-1]))
                    
                    seen_teams.append(team)
                
            slate_player_data += '{},{},{},{},{}\n'.format(slate_name, player_id, name, positions, salary)
                
                
# print(slate_player_data)
# print(player_data)
# print(team_data)
# print(slate_data)
    
write_file(slate_player_data, 'slate_player_data')
write_file(team_data, 'team_data')
write_file(player_data, 'player_data')
write_file(slate_data, 'slate_data')