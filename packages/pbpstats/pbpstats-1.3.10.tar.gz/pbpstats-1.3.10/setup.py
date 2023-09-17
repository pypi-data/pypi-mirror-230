# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbpstats',
 'pbpstats.data_loader',
 'pbpstats.data_loader.data_nba',
 'pbpstats.data_loader.data_nba.boxscore',
 'pbpstats.data_loader.data_nba.enhanced_pbp',
 'pbpstats.data_loader.data_nba.pbp',
 'pbpstats.data_loader.data_nba.possessions',
 'pbpstats.data_loader.data_nba.schedule',
 'pbpstats.data_loader.live',
 'pbpstats.data_loader.live.boxscore',
 'pbpstats.data_loader.live.enhanced_pbp',
 'pbpstats.data_loader.live.pbp',
 'pbpstats.data_loader.live.possessions',
 'pbpstats.data_loader.live.schedule',
 'pbpstats.data_loader.stats_nba',
 'pbpstats.data_loader.stats_nba.boxscore',
 'pbpstats.data_loader.stats_nba.enhanced_pbp',
 'pbpstats.data_loader.stats_nba.league_game_log',
 'pbpstats.data_loader.stats_nba.pbp',
 'pbpstats.data_loader.stats_nba.possessions',
 'pbpstats.data_loader.stats_nba.scoreboard',
 'pbpstats.data_loader.stats_nba.shots',
 'pbpstats.data_loader.stats_nba.summary',
 'pbpstats.objects',
 'pbpstats.resources',
 'pbpstats.resources.boxscore',
 'pbpstats.resources.enhanced_pbp',
 'pbpstats.resources.enhanced_pbp.data_nba',
 'pbpstats.resources.enhanced_pbp.live',
 'pbpstats.resources.enhanced_pbp.stats_nba',
 'pbpstats.resources.games',
 'pbpstats.resources.pbp',
 'pbpstats.resources.possessions',
 'pbpstats.resources.shots']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'pbpstats',
    'version': '1.3.10',
    'description': 'A package to scrape and parse NBA, WNBA and G-League play-by-play data',
    'long_description': None,
    'author': 'dblackrun',
    'author_email': 'darryl.blackport@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
