import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import scripts_util

import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
import utils


cookies = {
    '_gcl_au': '1.1.2065836015.1707942740',
    '_ga': 'GA1.2.574788829.1707942741',
    '__insp_uid': '2024603148',
    '__stripe_mid': 'db61d656-fba2-4b77-9ecb-3831a5c64f7b57cfeb',
    'pbid': 'c5005c5fc4e5521f514309e394f33ab69dbb836b3f153f987563682719a3293b',
    'PHPSESSID': '5804etafeaggeqe8c070uuett7',
    'pys_start_session': 'true',
    'pys_advanced_form_data': '%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D',
    '_fbp': 'fb.1.1708722628867.1967481615',
    '_gid': 'GA1.2.1228773083.1710293731',
    'pys_first_visit': 'true',
    'pysTrafficSource': 'direct',
    'pys_landing_page': 'https://www.dfscrunch.com/register/',
    'last_pysTrafficSource': 'direct',
    'last_pys_landing_page': 'https://www.dfscrunch.com/register/',
    'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1713133194%7C60T2PHunGweDWYpy7dExeDKpjBDQetWXA80okJrIZCi%7C0928efce9ad814c6252873415809067769f0c631a30402e9b6abf26c93efe0ec',
    '_gat': '1',
    '__insp_wid': '454073064',
    '__insp_nv': 'false',
    '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs',
    '__insp_targlpt': 'RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
    '__insp_identity': 'YW1s',
    '__insp_sid': '2436741901',
    '__stripe_sid': '685e93a8-ac79-4cb7-80e6-e81e401a8044f17722',
    '_ga_828EVXX1Q3': 'GS1.2.1710594732.68.1.1710594740.0.0.0',
    '__insp_slim': '1710594740781',
    '__insp_pad': '2',
}

headers = {
    'authority': 'www.dfscrunch.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,he;q=0.8',
    # 'cookie': '_gcl_au=1.1.2065836015.1707942740; _ga=GA1.2.574788829.1707942741; __insp_uid=2024603148; __stripe_mid=db61d656-fba2-4b77-9ecb-3831a5c64f7b57cfeb; pbid=c5005c5fc4e5521f514309e394f33ab69dbb836b3f153f987563682719a3293b; PHPSESSID=5804etafeaggeqe8c070uuett7; pys_start_session=true; pys_advanced_form_data=%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D; _fbp=fb.1.1708722628867.1967481615; _gid=GA1.2.1228773083.1710293731; pys_first_visit=true; pysTrafficSource=direct; pys_landing_page=https://www.dfscrunch.com/register/; last_pysTrafficSource=direct; last_pys_landing_page=https://www.dfscrunch.com/register/; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1713133194%7C60T2PHunGweDWYpy7dExeDKpjBDQetWXA80okJrIZCi%7C0928efce9ad814c6252873415809067769f0c631a30402e9b6abf26c93efe0ec; _gat=1; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=2436741901; __stripe_sid=685e93a8-ac79-4cb7-80e6-e81e401a8044f17722; _ga_828EVXX1Q3=GS1.2.1710594732.68.1.1710594740.0.0.0; __insp_slim=1710594740781; __insp_pad=2',
    'referer': 'https://www.dfscrunch.com/tool/nba/fanduel',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

def querySlateData(slate_id, site):
  params = {
    'currentPage': '1',
    'pageSize': '20',
    'site': site,
    'slate': slate_id,
  }

  response = requests.get('https://www.dfscrunch.com/api/v1/nba/players/', params=params, cookies=cookies, headers=headers)
  
  return response.json()

def querySlates(site, date):

  params = {
      'source': site,
      'timestamp': '{}T00:00:00-05:00'.format(date),
  }

  response = requests.get('https://www.dfscrunch.com/api/v1/nba/slates/', params=params, cookies=cookies, headers=headers)
  return response.json()
  

cannonical_slates = ['fd99589'] # TODO remember to update this

date = utils.date_str()
# date = '2024-02-22'
sites = [('fanduel', 'FD'), ('draftkings', 'DK')]
# sites = [('draftkings', 'DK')]
# sites = [('fanduel', 'FD')]

slate_data = []
team_data = []
seen_teams = []
resolved_statuses = []

def convert_time_string(time_string):
    timestamp1 = datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S%z')
    timestamp2 = timestamp1.astimezone(ZoneInfo('US/Eastern'))
    hour = timestamp2.hour - 12
    minute = timestamp2.minute
    
    return f'{hour:02}:{minute:02}pm ET'

for (site, site_key) in sites:
  slates = querySlates(site, date)
  for slate in slates:
    slate_player_data = []
    print(slate)
    slate_id = slate['id']
    
    slate_name = slate['name']
    timestamp1 = slate['timestamp']
    time_string = convert_time_string(timestamp1)
    
    time.sleep(3)
    
    players = querySlateData(slate_id, site)
    
    for player in players:
      player_id = player['site_id']
      name = player['name'].split(' : ')[0]
      
      team = player['team_home']
      team = utils.normalize_team_name(team)
      opp = player['team_away']
      opp = utils.normalize_team_name(opp)
      start_at = player['start_at']
      start_time = convert_time_string(start_at)
      
      projected = player['pfp']
      if slate_id in cannonical_slates and float(projected) == 0 and name not in resolved_statuses:
        resolved_statuses.append(f'{name},{team},{site},O')
      
      if team not in seen_teams:
        seen_teams.append(team)
        team_data.append(f'{team},{opp},{start_time}')
      
      salary = player['salary']
      pos = player['position']
      status = player['status']
      
      if site == 'fanduel' and (pos == 'MVP' or pos == 'STAR' or pos == 'PRO'):
        continue
      if site == 'draftkings' and pos == 'CPT':
        player_id = player['cpt_site_id']
    
      slate_player_data.append(f'{player_id},{name},{pos},{salary},{team}')
    
    if len(slate_player_data) == 0:
      continue
    
    slate_data.append(f'{site_key} {slate_name} {time_string},{site_key},{slate_id}')
    to_write = '\n'.join(slate_player_data)
    file_name = f'slate_player_data_{date}_{slate_id}'
    scripts_util.write_file(to_write, file_name)

to_write = '\n'.join(slate_data)
scripts_util.write_file(to_write, f'slate_data_{date}')
print(slate_data)

scripts_util.write_file('\n'.join(team_data), f'team_data_{date}')

# scripts_util.write_file('\n'.join(resolved_statuses), 'player_statuses')
