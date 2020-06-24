#!/usr/bin/env/python

import json
import sys
import requests
from pprint import pprint

instances = list(range(5, 15))

blacklisted_turkerids = set(["debugfollow", "debug"])
json_data = []
for instance in instances:
  r = requests.get(
      'https://vulcan.multicomp.cs.cmu.edu:9001/annotations/' + str(instance),
      verify=False)
  json_instance = r.json()
  json_instance["actions"] = []
  if json_instance["turkerid"] not in blacklisted_turkerids:
    json_data.append(json_instance)

with open(sys.argv[1], 'w') as outfile:
  json.dump(json_data, outfile)
