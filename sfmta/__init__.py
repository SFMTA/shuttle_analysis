# Make these available under the sfmta namespace:
from .sql_queries import (db_connect, get_all_shuttles,
                          get_points_for_shuttle, get_shuttles_companies)

from .application import main
