from .pp_scraper import PPScraper
from .caesars_scraper import CaesarsScraper

def scrape(sport, site, scrape_time):
  print(site)

  if site == 'PrizePicks':
    scraper = PPScraper(sport)
  elif site == 'Caesars':
    scraper = CaesarsScraper(sport)
  else:
    assert False

  result = scraper.run(scrape_time)

  return result
