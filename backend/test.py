from tinydb import TinyDB, Query, where
import sys
sys.path.append('/Users/amichailevy/Documents/spikes/dfs_web/backend/source/')
import utils
import optimizer
import data_utils

sport = 'NBA'

new_projections_fd = data_utils.get_current_projections(sport)
# new_projections_dk = data_utils.get_current_projections(sport, 'dk')

new_projections_fd_2 = data_utils.get_current_projections_persisted()

import pdb; pdb.set_trace()

