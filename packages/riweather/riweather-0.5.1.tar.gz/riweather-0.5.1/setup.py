# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['riweather', 'riweather.db', 'riweather.resources']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'pandas>=2.1.0,<3.0.0',
 'pyproj>=3.4.1,<4.0.0',
 'pyshp>=2.3.1,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'shapely>=2.0.0,<3.0.0',
 'sqlalchemy>=2.0.20,<3.0.0']

extras_require = \
{'plots': ['matplotlib>=3.6.2,<4.0.0', 'folium>=0.14.0,<0.15.0']}

entry_points = \
{'console_scripts': ['riweather = riweather.cli:main']}

setup_kwargs = {
    'name': 'riweather',
    'version': '0.5.1',
    'description': 'Grab publicly available weather data',
    'long_description': '# riweather\n\n[![Tests](https://github.com/ensley-nexant/riweather/workflows/Tests/badge.svg)](https://github.com/ensley-nexant/riweather/actions?workflow=Tests)\n[![Codecov](https://codecov.io/gh/ensley-nexant/riweather/branch/main/graph/badge.svg)](https://codecov.io/gh/ensley-nexant/riweather)\n[![Release](https://github.com/ensley-nexant/riweather/actions/workflows/release.yml/badge.svg)](https://github.com/ensley-nexant/riweather/actions/workflows/release.yml)\n\nGrab publicly available weather data with `riweather`. [See the full documentation](https://ensley-nexant.github.io/riweather).\n\n## Installation\n\nInstall with pip:\n\n```\npip install riweather\n```\n\nTo create interactive maps of weather station locations, install the package along with its optional dependencies:\n\n```\npip install riweather[plots]\n```\n\n## Usage\n\nGiven a latitude and longitude, get a list of weather stations sorted from nearest to farthest from that location.\n\n```python\n>>> import riweather\n\n>>> station_rank = riweather.rank_stations(39.98, -105.13, max_distance_m=20000)\n```\n\nSelect the top station (or a different station):\n\n```python\n>>> station = riweather.select_station(station_rank, rank=0)\n```\n\nView information about that station:\n\n```python\n>>> station.name, station.usaf_id\n```\n\nAnd pull weather data from that station for a certain year.\n\n```python\n>>> station.fetch_temp_data(2022)\n```\n',
    'author': 'John Ensley',
    'author_email': 'jensley@resource-innovations.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/ensley-nexant/riweather',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
