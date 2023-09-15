# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['energypylinear',
 'energypylinear.accounting',
 'energypylinear.assets',
 'energypylinear.results']

package_data = \
{'': ['*']}

install_requires = \
['PuLP>=2.7.0,<3.0.0',
 'markdown-include>=0.8.1,<0.9.0',
 'matplotlib>=3.6.2,<4.0.0',
 'numpy>=1.23.4,<2.0.0',
 'pandas>=1.5.2,<2.0.0',
 'pandera>=0.14.5,<0.15.0',
 'pydantic>=1.10.2,<2.0.0',
 'rich>=12.0.0,<13.0.0',
 'seaborn>=0.12.2,<0.13.0',
 'structlog>=23.1.0,<24.0.0']

setup_kwargs = {
    'name': 'energypylinear',
    'version': '0.2.1',
    'description': 'Optimizing energy assets with mixed-integer linear programming.',
    'long_description': '# energy-py-linear\n\n<img src="./static/coverage.svg"> [![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)\n\n---\n\nDocumentation: [energypylinear.adgefficiency.com](https://energypylinear.adgefficiency.com/latest)\n\n---\n\nA Python library for optimizing energy assets with mixed-integer linear programming:\n\n- electric batteries,\n- combined heat & power (CHP) generators,\n- electric vehicle smart charging.\n\nAssets can be optimized to either maximize profit or minimize carbon emissions.  \n\nEnergy balances are performed on electricity, high & low temperature heat.\n\n## Setup\n\nRequires Python 3.10+:\n\n```shell-session\n$ pip install energypylinear\n```\n\n## Quick Start\n\n### Asset API\n\nThe asset API allows optimizing a single asset at once.\n\nWe can optimize an electric battery operating in wholesale price arbitrage using `epl.Battery`:\n\n```python\nimport energypylinear as epl\n\n#  2.0 MW, 4.0 MWh battery\nasset = epl.battery.Battery(power_mw=2, capacity_mwh=4, efficiency=0.9)\n\nresults = asset.optimize(\n  electricity_prices=[100.0, 50, 200, -100, 0, 200, 100, -100]\n)\n```\n\nSee how to optimize other asset types in [how-to/optimize-assets](https://energypylinear.adgefficiency.com/latest/how-to/dispatch-assets/). \n\n### Site API\n\nThe site API allows optimizing multiple assets at once:\n\n```python\nimport energypylinear as epl\n\nsite = epl.Site(assets=[\n  #  2.0 MW, 4.0 MWh battery\n  epl.Battery(power_mw=2.0, capacity_mwh=4.0),\n  #  30 MW generator\n  epl.Generator(\n    electric_power_max_mw=100,\n    electric_power_min_mw=30,\n    electric_efficiency_pct=0.4\n  ),\n  #  2 EV chargers & 4 charge events\n  epl.EVs(\n      chargers_power_mw=[100, 100],\n      charge_events_capacity_mwh=[50, 100, 30, 40],\n      charge_events=[\n          [1, 0, 0, 0, 0],\n          [0, 1, 1, 1, 0],\n          [0, 0, 0, 1, 1],\n          [0, 1, 0, 0, 0]\n      ]\n  )\n])\n\nresults = site.optimize(\n  electricity_prices=[100, 50, 200, -100, 0],\n  high_temperature_load_mwh=[105, 110, 120, 110, 105],\n  low_temperature_load_mwh=[105, 110, 120, 110, 105]\n)\n```\n\nThe site API will optimize the assets together, and return the results for each asset. \n\n### Examples\n\nExamples as independent scripts are `./examples`:\n\n```shell\n$ ls ./examples\n./examples\n├── battery.py\n├── chp.py\n├── evs.py\n└── forecast-accuracy.py\n```\n\n## Test\n\n```shell\n$ make test\n```\n\n## Documentation \n\nHosted at [energypylinear.adgefficiency.com/latest](https://energypylinear.adgefficiency.com/latest).\n',
    'author': 'Adam Green',
    'author_email': 'adam.green@adgefficiency.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.12',
}


setup(**setup_kwargs)
