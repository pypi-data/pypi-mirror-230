#!/usr/bin/env python3

"""
Grafana dashboard exporter

The exported dashboards are saved in a directory 'exported-dashboards-<datetime>'
"""

import json
import os
from pathlib import Path
from rich import print_json

import requests

from egse.system import format_datetime

HOST = 'http://lin-plato-2.sron.rug.nl:3000'
API_KEY = os.environ["GRAFANA_API_KEY"]

DIR = f'exported-dashboards-{format_datetime(fmt="%Y%m%d%H%M%S")}'


def main():
    headers = {'Authorization': f'Bearer {API_KEY}'}
    response = requests.get(f'{HOST}/api/search?query=&', headers=headers)
    response.raise_for_status()
    dashboards = response.json()
    # print_json(data=dashboards)

    if not os.path.exists(DIR):
        print(f"Creating folder {DIR}")
        os.makedirs(DIR)

    for dashboard in dashboards:
        response = requests.get(f"{HOST}/api/dashboards/uid/{dashboard['uid']}", headers=headers)
        # print_json(data=response.json())
        data = response.json()['dashboard']
        dash = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
        name = data['title'].replace(' ', '_').replace('/', '_').replace(':', '').replace('[', '').replace(']', '').replace('.', '_')

        print(f"Saving: {dashboard['title']} as {name}")

        with open(Path(DIR,  name).with_suffix('.json'), 'w') as fd:
            fd.write(dash)
            fd.write('\n')


if __name__ == '__main__':
    main()
