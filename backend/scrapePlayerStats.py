import requests
import json

result = requests.get('https://www.nba.com/game/mia-vs-phi-0022300985/box-score')

json_text = result.text.split('<script id="__NEXT_DATA__" type="application/json">')[1].split('</script>')[0]
as_json = json.loads(json_text)

home_players = as_json['props']['pageProps']['game']['homeTeam']['players']
away_players = as_json['props']['pageProps']['game']['awayTeam']['players']
all_players = home_players + away_players

for player in all_players:
  name = player['firstName'] + ' ' + player['familyName']
  stats = player['statistics']
  threePts = stats['threePointersMade']
  rebounds = stats['reboundsTotal']
  assists = stats['assists']
  steals = stats['steals']
  blocks = stats['blocks']
  turnovers = stats['turnovers']
  personalFouls = stats['foulsPersonal']
  points = stats['points']
  print(f'{name} 3pt: {threePts} reb: {rebounds} ast: {assists} stl: {steals} blk: {blocks} to: {turnovers} pf: {personalFouls} pts: {points}')

