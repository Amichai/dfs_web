from tinydb import TinyDB, Query, where
import itertools
import requests
import json
import time
import csv
from tabulate import tabulate
import datetime

import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
import source.scraper as scraper
from name_mapper import dk_name_to_fd_name, team_names
from optimizer_library import NFL_Optimizer
import optimizer
import utils
import data_utils

import scripts_util

def upload():
    
    player_statuses = scripts_util.read_file('player_statuses').split('\n')
    player_statuses = [a for a in player_statuses if a != '']
    excluded_players = [a.split(',')[0] for a in player_statuses if a.split(',')[3] == 'O']
    gtd_players = [a.split(',')[0] for a in player_statuses if a.split(',')[3] == 'GTD']
    
    date_suffix = utils.date_str()
    current_player_data = scripts_util.read_file('player_data_{}'.format(date_suffix))
    lines = current_player_data.split('\n')
    name_to_row = {}
    for line in lines:
        parts = line.split(',')
        if len(parts) < 2:
            continue
        name = parts[0]
        status = parts[-1]
        name_to_row[name] = line


    # import pdb; pdb.set_trace()
    # assert False
    sport = 'NBA'
    scraper_name = 'Caesars'

    # TODO use data_utils.get_current_projections_persisted() to persist projections for started games
    initial_projections_fd = data_utils.get_current_projections(sport)
    initial_projections_dk = data_utils.get_current_projections(sport, 'dk')

    print(sport, scraper_name)

    today_date =  str(datetime.datetime.now()).split(' ')[0]
    file = open('DBs/{}/{}_{}.txt'.format(sport, scraper_name, today_date), 'a')
    file_most_recent = open('DBs/{}/{}_{}_current.txt'.format(sport, scraper_name, sport), 'w')

    scrape_time = str(datetime.datetime.now()).split('.')[0]
    utils.write_to_files('t:' + str(scrape_time) + '\n', file, file_most_recent)

    scrape_results = scraper.scrape(sport, scraper_name, scrape_time) # GAME DAY parameter here
    name_to_team = {}
    for scrape_result in scrape_results:
        team1 = scrape_result['team']
        name_to_team[scrape_result['name']] = team_names[team1]

    utils.write_to_files(",".join([str(a) for a in scrape_results[0].keys()]) + '\n', file, file_most_recent)

    for result in scrape_results:
        utils.write_to_files(",".join([str(a) for a in result.values()]) + '\n', file, file_most_recent)


    file.close()
    file_most_recent.close()

    player_data = []

    new_projections_fd = data_utils.get_current_projections(sport)
    new_projections_dk = data_utils.get_current_projections(sport, 'dk')
    diffs = []
    removed = []
    added = []

    news_feed_updates = [] # name, team, projectionfd, projectiondk, status?

    current_time = time.time()
    seen_player_names = []

    for key in set(initial_projections_fd.keys()).union(new_projections_fd.keys()):
        initial_projection_fd = initial_projections_fd.get(key)
        initial_projection_dk = initial_projections_dk.get(key)
        new_fd_projection = new_projections_fd.get(key)
        new_dk_projection = new_projections_dk.get(key)

            
        
        if new_fd_projection != None:
            if not key in seen_player_names:
                seen_player_names.append(key)
            
            team = name_to_team[key]
            if key in excluded_players:
                player_data.append('{},{},{},{},{}'.format(key, team, 0, 0, 'O'))
            else:
                status = ''
                if key in gtd_players:
                    status = 'GTD'
                player_data.append('{},{},{},{},{}'.format(key, team, new_fd_projection, new_dk_projection, status))
            
        
        if initial_projection_fd == None:
            team = name_to_team[key]
            
            added.append((key, new_fd_projection))
            news_feed_updates.append((key, team, '', '', new_fd_projection, new_dk_projection))
        if new_fd_projection == None:
            removed.append((key, initial_projection_fd))
        if initial_projection_fd != None and new_fd_projection != None and float(new_fd_projection) != float(initial_projection_fd):
            team = name_to_team[key]
            
            diff = float(new_fd_projection) - float(initial_projection_fd)
            if abs(diff) > 0.01:
                diffs.append((key, new_fd_projection, diff))
            
            if abs(diff) > 0.5: # significant change, pass it along
                news_feed_updates.append((key, team, initial_projection_fd, initial_projection_dk, new_fd_projection, new_dk_projection))

    diffs_sorted = sorted(diffs, key=lambda a: abs(a[2]), reverse=True)
    print(tabulate(diffs_sorted, headers=['Name', 'new', 'diff']))

    added_sorted = sorted(added, key=lambda a: a[1], reverse=True)
    if len(added_sorted) > 0:
        print(tabulate(added_sorted, headers=['Name', 'projection']))

    removed_sorted = sorted(removed, key=lambda a: a[1], reverse=True)
    if len(removed_sorted) > 0:
        print("Removed: {}".format(",".join([a[0] for a in removed_sorted])))
        # this is where we should be persistiting the removed players to player_data
        # for removed in removed_sorted:
        #     name = removed[0]
        #     if name in name_to_row:
        #         line = name_to_row[name]
        #         player_data.append(line)
                
    for name in name_to_row.keys():
        if name not in seen_player_names:
            line = name_to_row[name]
            player_data.append(line)
    
    
    news_feed_file_name = 'news_feed_{}'.format(date_suffix)

    current_news_feed = scripts_util.read_file(news_feed_file_name)
    # current_news_feed = ''

    news_feed_string = "{}{}, {}".format(current_news_feed, current_time, json.dumps(news_feed_updates)) + '\n'

    #upload news feed
    # upload player projections and status

    scripts_util.write_file(news_feed_string, news_feed_file_name)
    out_players = []

    scripts_util.write_file("\n".join(player_data), 'player_data_{}'.format(date_suffix))

    scripts_util.increment_feed_version()
    
if __name__ == "__main__":
    upload()