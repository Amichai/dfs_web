from tinydb import TinyDB, Query, where
import itertools
import requests
import json
import time
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import csv

import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
from name_mapper import dk_name_to_fd_name
from optimizer_library import NFL_Optimizer
import optimizer
import utils
import os
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
    try:
        bucket_name = 'amichai-dfs-data'  # S3 bucket name
        result = s3.put_object(Body=content, Bucket=bucket_name, Key=name)
        print(result)
    except ClientError as e:
        # Handles errors from the service itself, such as incorrect bucket permissions
        print('ClientError writing file {}: {}'.format(name, e))
    except BotoCoreError as e:
        # Handles errors in the boto3 framework, such as network errors
        print('BotoCoreError writing file {}: {}'.format(name, e))
    except Exception as e:
        # Generic catch-all for any other exceptions
        print('Unexpected error writing file {}: {}'.format(name, e))

# date = '2023-11-22'
date = utils.date_str()

# we should actually pull this from the `current` table on any given day
lines = data_utils.get_scraped_lines_for_date('Caesars', date)
name_to_projection_fd = data_utils.scraped_lines_to_projections(lines, 'fd')
name_to_projection_dk = data_utils.scraped_lines_to_projections(lines, 'dk')


def lookup_projection(name, site):
    if site == 'fd':
        if not name in name_to_projection_fd:
            return 0.0
        return name_to_projection_fd[name]
    elif site == 'dk':
        if name in dk_name_to_fd_name:
            name = dk_name_to_fd_name[name]
        if not name in name_to_projection_dk:
            return 0.0
        return name_to_projection_dk[name]
    else:
        raise Exception('invalid site {}'.format(site))    

path = './DBs/NBA/slates_' + date + '.txt'

fd_names = {}

# to upload
# [slate name, player id, player name, pos, salary]
slate_player_data = ''
# [name, team, projection, status]
player_data = ''
# [team, start_time, opp]
team_data_array = []
#[slate name, site]
slate_data = ''

download_folder = '/Users/amichailevy/Downloads/'

path_and_slate_names = [
    ('FanDuel-NBA-2023 ET-12 ET-19 ET-97437-players-list.csv', 'FD Main 7:30'),
    ('FanDuel-NBA-2023 ET-12 ET-19 ET-97438-players-list.csv', 'FD SA@MIL 8:00'),
    ('FanDuel-NBA-2023 ET-12 ET-19 ET-97439-players-list.csv', 'FD BOS@GS 10:00'),
    ('FanDuel-NBA-2023 ET-12 ET-19 ET-97445-players-list.csv', 'FD After Hours 10:00'),

    ('DKSalaries (11).csv', 'DK Main 7:30'),
    ('DKSalaries (12).csv', 'DK MEM@NOP 7:30'),
    ('DKSalaries (13).csv', 'DK SAS@MIL 8:00'),
    ('DKSalaries (14).csv', 'DK After Hours 10:00'),
    ('DKSalaries (15).csv', 'DK BOS@GSW 10:00'),
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
                    projection_fd = lookup_projection(name, 'fd')
                    projection_dk = lookup_projection(name, 'dk')
                    
                    player_data += '{},{},{},{},{}\n'.format(name, team, projection_fd, projection_dk, status)
                    seen_player_ids.append(player_id)
            elif is_dk:
                positions = row[0]
                name = row[2]
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
                    game_info = '{},{},{}\n'.format(team_normalized, opp_normalized, '{} {}'.format(game_parts[-2], game_parts[-1]))
                    if not game_info in team_data_array:
                        team_data_array += [game_info]
                    
                    seen_teams.append(team)
                
            slate_player_data += '{},{},{},{},{}\n'.format(slate_name, player_id, name, positions, salary)
                
                
print(team_data_array)
team_data_sorted = sorted(team_data_array, key=lambda x: x.split(',')[2])
team_data = ''.join(team_data_sorted)
# print(slate_player_data)
# print(player_data)
print("team data", team_data)
print("slate data", slate_data)

# import pdb; pdb.set_trace()
    
write_file(slate_player_data, 'slate_player_data')
write_file(player_data, 'player_data')
write_file(team_data, 'team_data')
write_file(slate_data, 'slate_data')