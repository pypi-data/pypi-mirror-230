# -*- coding: utf8 -*-

"""
Importació de services des de json.
"""

import json
import os


json_path = os.path.dirname(os.path.abspath(__file__))
json_file = '{}/services.json'.format(json_path)
json_data = json.load(open(json_file))

DB_INSTANCES = json_data['db_instances']
if os.environ["HOST"] == "X0002":
    for key, values in DB_INSTANCES.items():
        if "p2262" in key:
            values["host"] = "10.80.217.84"
            values["local_infile"] = False
DB_CREDENTIALS = json_data['db_credentials']
REDIS_INSTANCES = json_data['redis_instances']
MAIL_SERVERS = json_data['mail_servers']
SSH_SERVERS = json_data['ssh_servers']
TRELLO_CREDENTIALS = json_data['trello']
