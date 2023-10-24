import requests
from selenium import webdriver
from datetime import timedelta, date
import dateutil.parser
import utils
import json
import time
from selenium.webdriver.common.by import By


known_sports = ["NBA","WNBA","MLB","NFL","MMA","CFB","PGA", "NHL"]

class CaesarsScraper:
  def __init__(self, sport, isGameday=True):
    self.sport = sport
    self.sport_lookup = self.sport
    if self.sport_lookup == "CFB":
      self.sport_lookup = "NCAAF"

    self.name = 'Caesars'
    self.isGameday = isGameday

    # assert sport in known_sports
    self.game_guids = None
    if sport == 'NBA' or sport == 'WNBA':
      self.sport_name = "basketball"
    elif sport == "MLB":
      self.sport_name = "baseball"
    elif sport == "NFL" or sport == "CFB":
      self.sport_name = "americanfootball"
    elif sport == "MMA":
      self.sport_name = "ufcmma"
    elif sport == "PGA":
      self.sport_name = "golf"
      self.sport_lookup = "Shriners Children's Open"
    elif sport == "NHL":
      self.sport_name = "icehockey"
      

    self.driver = utils.get_chrome_driver()
    self.all_team_names = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers","Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers","Los Angeles Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat","Milwaukee Bucks","Minnesota Timberwolves","New Orleans Pelicans","New York Knicks","Oklahoma City Thunder","Orlando Magic","Philadelphia 76ers","Phoenix Suns","Portland Trail Blazers","Sacramento Kings","San Antonio Spurs","Toronto Raptors","Utah Jazz","Washington Wizards"]

  def _get_game_guids_today(self):
    # url = "https://www.williamhill.com/us/nj/bet/api/v3/sports/{}/events/schedule".format(self.sport_name)
    url = "https://api.americanwagering.com/regions/us/locations/nj/brands/czr/sb/v3/sports/{}/events/schedule".format(self.sport_name)
    print(url)
    # result = requests.get(url)
    as_json  = utils.get_with_selenium(url)

    id_to_start_time = {}
    # print(result)
    # as_json = result.json()

    # __import__('pdb').set_trace()
    all_sports = [a['name'] for a in as_json['competitions']]

    target_index = 0
    if self.sport_lookup in all_sports:
      target_index = all_sports.index(self.sport_lookup)
    else:
      print("WARNING SPORT NOT FOUND: {}, {}".format(self.sport, self.sport_lookup))

    events = as_json['competitions'][target_index]['events']
  
    counter = 1
    all_start_times = []
    to_return = []
    for event in events:
        event_id = event["id"]


        name = event["name"]
        start_time = event["startTime"]
        id_to_start_time[event_id] = start_time
        start_time_parsed = dateutil.parser.isoparse(start_time)
        time_shifted = start_time_parsed - timedelta(hours=4)
        today = date.today()

        all_start_times.append(start_time)

        if not self.isGameday and abs(today.day - time_shifted.day) < 7 and today.month == time_shifted.month:
          counter += 1
          print("{} - {}, {}, {}".format(counter, name, time_shifted.strftime('%m/%d %H:%M'), event_id))
          to_return.append(event_id)
        elif self.isGameday and time_shifted.day == today.day and time_shifted.month == today.month:
          counter += 1
          print("{} - {}, {}, {}".format(counter, name, time_shifted.strftime('%m/%d %H:%M'), event_id))
          to_return.append(event_id)

    return to_return, id_to_start_time

  def run(self, scrape_time):
    whitelisted_stats = ['Points', 'Rebounds', 'Assists', 'Steals', 'Blocks', 'Turnovers',  
                         "Points + Assists + Rebounds", 
                         "Points + Assists",
                         "Points + Rebounds",
                         "Rebounds + Assists",
                         "Blocks + Steals"
                         ]

    filtered_stats = []

    projections = []

    if self.game_guids == None:
      self.game_guids, id_to_start_time = self._get_game_guids_today()

    for guid in self.game_guids:
      print("GUID: {}".format(guid))
      url = "https://api.americanwagering.com/regions/us/locations/nj/brands/czr/sb/v3/events/{}".format(guid)

      self.driver.get(url)

      time.sleep(1.0)

      # as_text = self.driver.find_element('tag', 'body').text
      as_text = self.driver.find_element(By.CSS_SELECTOR, 'body').text


      as_json = json.loads(as_text)
      if not 'markets' in as_json:
        __import__('pdb').set_trace()
        continue

      for market in as_json['markets']:
          selections = market['selections']
          if not 'name' in market:
            print('name not found in {}'.format(market))
            continue
          
          name = market['name']

          is_active = market['active']


          if name == None:
              continue
          if "|Alternative " in name or "|Margin of " in name:
              continue

          if "Alternative" in str(market):
              # __import__('pdb').set_trace()
              continue


          # __import__('pdb').set_trace()
          name_parts = market['name'].split('| |')
          # if market['name'].count('|') == 2:
          #     continue
          # if len(name_parts) == 1:
          #     continue
          
          if " |Live|" in name:
              continue

          name = name_parts[0].strip('|')
          if name in self.all_team_names:
            continue

          if len(name_parts) > 1:
            stat = name_parts[1].strip('|').replace('Total ', '')
            if stat == "3pt Field Goals":
              continue
          else:
            stat = name_parts[0]


          if stat not in whitelisted_stats:
             if not stat in filtered_stats:
                filtered_stats.append(stat)
                print('filtering: {}'.format(stat))
             continue
          
          under_faction = None
          over_fraction = None

          for selection in selections:
            if selection['price'] == None:
              continue

            if selection['type'] == 'under':
                under_faction = selection['price']['d']
            elif selection['type'] == 'over':
                over_fraction = selection['price']['d']
            elif selection['type'] == 'home':
                under_faction = selection['price']['d']
            elif selection['type'] == 'away':
                over_fraction = selection['price']['d']
          
          if under_faction == None or over_fraction == None:
              continue

          odds1 = over_fraction
          odds2 = under_faction

          odds1 = 1.0 / odds1
          odds2 = 1.0 / odds2

          odds_percentage = odds1 / (odds1  + odds2)
          
          if not 'line' in market:
             continue

          line = market['line']
          # print(market)
          startTime = id_to_start_time[guid]
  
          line_adjusted = round(float(line) + (float(odds_percentage) - 0.5) * float(line), 3)

          team = ''
          if 'metadata' in market and 'teamName' in market['metadata']:
            team = market['metadata']['teamName'].strip('|')

          projections.append({
            "line_score": line_adjusted,
            "stat": stat,
            "start_time": startTime,
            "eventId": guid,
            "line_original": line,
            "under_fraction": under_faction,
            "over_fraction": over_fraction,
            "active": is_active,
            "name": name,
            "time": scrape_time,
            "team": team,
            "line_id": "{}_{}_{}".format(name, stat, startTime)
        })
        
    return projections
