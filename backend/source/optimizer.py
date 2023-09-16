from name_mapper import name_mapper_pp_to_fd, name_mapper
import utils
from optimizer_library import DK_NBA_Optimizer
import itertools

def normalize_name(name):
    if name in name_mapper:
        name = name_mapper[name]

    return name


def get_player_pool(name_stat_to_val, seen_names, slate_lines):
  player_pool = []

  for name in seen_names:
      unmapped_name = name
      if name in name_mapper_pp_to_fd:
          name = name_mapper_pp_to_fd[name]
      # if name == "D.K. Metcalf":
      #     name = "DK Metcalf"

      if 'DST' in name:
          parsed_name = name.split(' ')[0]
          matched_names = [a for a in slate_lines if parsed_name in a['name']]
      else:
          matched_names = [a for a in slate_lines if a['name'] == name]

      if len(matched_names) == 0:
          print("Missing projection for: ", name)
          assert name != "D.K. Metcalf"
          continue
      
      # fantasy_score = 0
      if len(matched_names) > 1:
        salary1 = float(matched_names[0]['salary'])
        salary2 = float(matched_names[1]['salary'])
        salary = min(salary1, salary2)
        assert len(matched_names) == 2
      else:
        salary = float(matched_names[0]['salary'])


      position = matched_names[0]['position']
      team = matched_names[0]['team']
      
      proj = None

      key1 = "{}_{}".format(unmapped_name, "Fantasy Score")
      key2 = "{}_{}".format(unmapped_name, "FSComputed")
      if key1 in name_stat_to_val:
          proj = name_stat_to_val[key1]
      if key2 in name_stat_to_val:
          proj = name_stat_to_val[key2]

      if proj is None:
          continue
      
      # print("{},{},{}".format(name, salary, proj))
      # fantasy_score = 
      # get the player cost

      player_pool.append([name, salary, proj, position, team])
  return player_pool

def optimize_NFL_FD_single_game(slate_players, scraped_lines):
    pass

def get_player_projection_data(scraped_lines, teams_to_include):
      
    seen_names = []
    seen_stats = []

    name_to_stats = {}
    name_stat_to_val = {}

    for result in scraped_lines:
        name = result['name']
        line = result['line_score']
        team = result['team']
        stat = result['stat']
        if teams_to_include and team not in teams_to_include:
            continue
        
        if not name in name_to_stats:
            name_to_stats[name] = [stat]
        else:
            name_to_stats[name].append(stat)

        name_stat = "{}_{}".format(name, stat)
        name_stat_to_val[name_stat] = line

        if not name in seen_names:
            seen_names.append(name)

        if not stat in seen_stats:
            seen_stats.append(stat) 


    computed_stats = [
      # {
      #   'name': 'FSComputed', # for QBs missing a fantasy score
      #   'stats': ['Pass Yards', 'Pass TDs', 'Rush Yards'],
      #   'weights': [0.04, 4, 0.1]
      # },
      # {
      #   'name': 'FSComputed', # for QBs missing a fantasy score
      #   'stats': ['Pass Yards', 'Pass+Rush+Rec TDs', 'Rush Yards'],
      #   'weights': [0.04, 4, 0.1]
      # },
      {
        'name': 'FSComputed',
        'stats': ['Fantasy Score', 'Receptions'],
        'weights': [1, -0.5]
      },
      {
        'name': 'FSComputed',
        'stats': ['Kicking Points'],
        'weights': [1]
      },
    ]

    for name, stats in name_to_stats.items():
        for computed_stat in computed_stats:
          computed_stat_name = computed_stat['name']
          if all([a in stats for a in computed_stat['stats']]):
              new_stat_name = "{}_{}".format(name, computed_stat_name)
              new_val = 0
              for i, stat in enumerate(computed_stat['stats']):
                  new_val += name_stat_to_val["{}_{}".format(name, stat)] * computed_stat['weights'][i]

              name_stat_to_val[new_stat_name] = new_val

              if not computed_stat_name in seen_stats:
                  seen_stats.append(computed_stat_name)

    print('', end=',')
    for stat in seen_stats:
        print(stat, end=',')
    print()

    for name in seen_names:
        print(name, end=',')
        for stat in seen_stats:
            name_stat = "{}_{}".format(name, stat)
            if name_stat in name_stat_to_val:
                print(name_stat_to_val[name_stat], end=',')
            else:
                print('', end=',')
        print()

    return name_stat_to_val, seen_names, seen_stats





def get_player_projection(scraped_lines, name):
    matched_players = [a for a in scraped_lines if a['name'].strip() == name]
    if len(matched_players) == 0:
        print("Missing projection for: ", name)
        return 0

    try:
        pts = [a for a in matched_players if a['stat'] == 'Points'][0]['line_score']
        # rebounds = [a for a in matched_players if a['stat'] == 'Rebounds'][0]['line_score']
    except:
        print("insufficient data for: ", name)
        return 0
    
    return float(pts)
    # return float(pts) + float(rebounds) * 1.5


def optimize_for_single_game_fd(all_players, ct, locks=None):
    all_rosters = []

    roster_keys = set()

    candidates = itertools.permutations(all_players, 5)
    for candidate in candidates:
        total_cost = sum(pl[1] for pl in candidate)
        if total_cost > 60000:
            continue
        
        p1 = candidate[0]
        p2 = candidate[1]
        p3 = candidate[2]
        p4 = candidate[3]
        p5 = candidate[4]

        # total_value = p1[2] * 2 + p2[2] * 1.5 +  p3[2] * 1.2 + p4[2] + p5[2]
        total_value = p1[2] * 1.5 + p2[2]+  p3[2] + p4[2] + p5[2]

        roster_key = "|".join(sorted([a[0] for a in candidate])) + "|" + str(round(total_value, 5))
        if roster_key in roster_keys:
            continue

        roster_keys.add(roster_key)
        all_rosters.append((candidate, total_value, total_cost))

    all_rosters_sorted = sorted(all_rosters, key=lambda a: a[1], reverse=True)
    to_return = all_rosters_sorted[:ct]
    for roster in to_return:
        print(roster)
        
    return to_return


def optimize_FIBA_dk(slate_players, scraped_lines):
    dk_positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

    # print(results)
    by_position = {}
    for slate_player in slate_players:
        # print(slate_player)
        name = slate_player['name'].strip()
        name = normalize_name(name)
        positions = slate_player['position'].split('/')
        salary = slate_player['salary']
        team = slate_player['team']
        projection = get_player_projection(scraped_lines, name)
        
        # projection += float(salary) / 11800 # prefer higher salary
        # projection += random.uniform(0, 1) / 1000 #this is necessary apparently
        if projection == 0:
            continue

        all_position = []

        for position in positions:
            # if not position in by_position:
            #     by_position[position] = []
            positions_extended = dk_positions_mapper[position]
            for pos in positions_extended:
                if not pos in all_position:
                    all_position.append(pos)
        
        for pos in all_position:
            if not pos in by_position:
                by_position[pos] = []
            
            by_position[pos].append(utils.Player(name, position, salary, team, projection))

    optimizer = DK_NBA_Optimizer()

    results = optimizer.optimize(by_position, None)

    print(results)


    return results
