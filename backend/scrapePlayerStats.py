import requests
import json

result = requests.get('https://www.nba.com/game/mia-vs-phi-0022300985/box-score')

json_text = result.text.split('<script id="__NEXT_DATA__" type="application/json">')[1].split('</script>')[0]
as_json = json.loads(json_text)

home_players = as_json['props']['pageProps']['game']['homeTeam']['players']
away_players = as_json['props']['pageProps']['game']['awayTeam']['players']
all_players = home_players + away_players

name_to_projections = {}

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
  # print(f'{name} 3pt: {threePts} reb: {rebounds} ast: {assists} stl: {steals} blk: {blocks} to: {turnovers} pf: {personalFouls} pts: {points}')
  fdfp = points + rebounds * 1.2 + assists * 1.5 + steals * 3 + blocks * 3 - turnovers
  
  double_digit_count = 0
  stat_set = [points, rebounds, assists, blocks, steals]
  for stat in stat_set:
    if stat >= 10:
      double_digit_count += 1
  
  performance_boost = 0
  if double_digit_count == 2:
    performance_boost = 1.5
  elif double_digit_count >= 3:
    performance_boost = 3
  
  dkfp = points + threePts * 0.5 + rebounds * 1.25 + assists * 1.5 + steals * 2 + blocks * 2 - (turnovers / 2.0) + performance_boost

  name_to_projections[name] = (fdfp, dkfp)
  
print(name_to_projections)

# write to db: playerId, date, fdfp, dkfp