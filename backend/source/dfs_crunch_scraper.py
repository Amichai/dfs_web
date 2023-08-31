import requests
import utils

query_parameters = {
    'cookies': {
    'pys_start_session': 'true',
    '_gcl_au': '1.1.1267622578.1667136773',
    'last_pys_landing_page': 'https://www.dfscrunch.com/',
    '_ga': 'GA1.2.698555203.1667136774',
    '_fbp': 'fb.1.1667136773620.1727448397',
    '__stripe_mid': '45055897-96ba-46bb-8cf3-16a336af06f4a6381a',
    'tk_ai': 'jetpack%3AmEAM9XamI7PIqp4FV%2FE35%2FLQ',
    'wordpress_test_cookie': 'WP%20Cookie%20check',
    'wp_lang': 'en_US',
    'last_pysTrafficSource': 'direct',
    '__insp_uid': '1266658190',
    'csrftoken': 'ZhLA3MIT5rPn4cbe1Rk1gAQo3Y6KdhFvaHIZL7CoWtHOy1LSrXJrggALMyvxs1Ru',
    'pys_first_visit': 'true',
    'pysTrafficSource': 'direct',
    'pys_landing_page': 'https://www.dfscrunch.com/',
    '_gid': 'GA1.2.459893526.1672318748',
    'pys_session_limit': 'true',
    '_gat_gtag_UA_170864106_1': '1',
    '__stripe_sid': '40efb37c-82dd-4ff0-abfc-beaade08354905349a',
    'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1674949487%7C9PvF5svFquY0gYZKDl2BkgZ4hexFt9VL0j2cg41jLiW%7Cf4219a64e0b188316d493d8f4cb3a5a2fa9d879c8c8e40127b37381c7fdaa230',
    'pys_advanced_form_data': '%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D',
    '_gat': '1',
    '__insp_wid': '454073064',
    '__insp_nv': 'false',
    '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs',
    '__insp_targlpt': 'RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
    '__insp_identity': 'YW1s',
    '__insp_norec_sess': 'true',
    '__insp_slim': '1672357499158',
  },

  'headers':{
    'authority': 'www.dfscrunch.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    # 'cookie': 'pys_start_session=true; _gcl_au=1.1.1267622578.1667136773; last_pys_landing_page=https://www.dfscrunch.com/; _ga=GA1.2.698555203.1667136774; _fbp=fb.1.1667136773620.1727448397; __stripe_mid=45055897-96ba-46bb-8cf3-16a336af06f4a6381a; tk_ai=jetpack%3AmEAM9XamI7PIqp4FV%2FE35%2FLQ; wordpress_test_cookie=WP%20Cookie%20check; wp_lang=en_US; last_pysTrafficSource=direct; __insp_uid=1266658190; csrftoken=ZhLA3MIT5rPn4cbe1Rk1gAQo3Y6KdhFvaHIZL7CoWtHOy1LSrXJrggALMyvxs1Ru; pys_first_visit=true; pysTrafficSource=direct; pys_landing_page=https://www.dfscrunch.com/; _gid=GA1.2.459893526.1672318748; pys_session_limit=true; _gat_gtag_UA_170864106_1=1; __stripe_sid=40efb37c-82dd-4ff0-abfc-beaade08354905349a; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1674949487%7C9PvF5svFquY0gYZKDl2BkgZ4hexFt9VL0j2cg41jLiW%7Cf4219a64e0b188316d493d8f4cb3a5a2fa9d879c8c8e40127b37381c7fdaa230; pys_advanced_form_data=%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D; _gat=1; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_norec_sess=true; __insp_slim=1672357499158',
    'referer': 'https://www.dfscrunch.com/tool/nba/fanduel',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
},
      
  'NBA': {
    'params': {
        'currentPage': '1',
        'pageSize': '20000',
        'site': 'fanduel',
    },
    'url': 'https://www.dfscrunch.com/api/v1/nba/players/'
  },

  'NFL': {
    'params': {
        'currentPage': '1',
        'pageSize': '20000',
        'site': 'fanduel',
    },
    'url': 'https://www.dfscrunch.com/api/v1/nfl/players/'
  },

  'WNBA': {
    'params': {
      'currentPage': '1',
      'pageSize': '20',
      'site': 'fanduel',
      'slate': 'fd76281',
    },
    'url': 'https://www.dfscrunch.com/api/v1/wnba/players'
  },
  
  'MLB': {
    'params': {
      'currentPage': '1',
      'pageSize': '20',
      'site': 'fanduel',
      'slate': 'fd76886',
    },
    'url':'https://www.dfscrunch.com/api/v1/mlb/players/'
  },
  
  'CBB': {
    'params': {
      'currentPage': '1',
      'pageSize': '20',
      'site': 'draftkings',
    },
    'url':' https://www.dfscrunch.com/api/v1/cbb/players'
  },
}


class DFSCrunchScraper:
  def __init__(self, sport, slate):
    self.sport = sport
    assert sport == "NBA" or sport == "MLB" or sport == "WNBA" or sport == "CBB" or sport == "NFL"
    self.name = 'DFSCrunch'
    self.slate = slate

  def run(self):
    to_return = {}
    all_players = []
    url = query_parameters[self.sport]['url']
    params = query_parameters[self.sport]['params']

    params['slate'] = self.slate
    headers = query_parameters['headers']
    cookies = query_parameters['cookies']

    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    all_players += response.json()
    print("Players: {}".format(len(all_players)))

    for player in all_players:
        name = player['name']
        proj = player['pfp']
        to_return[name] = {"Fantasy Score": proj}


    return to_return
