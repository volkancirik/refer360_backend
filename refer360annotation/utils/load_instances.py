#!/usr/bin/env/python

import json
import sys
import requests
from pprint import pprint


instances = json.load(open(sys.argv[1], 'r'))

for instance in instances:
  del instance['actions']
  del instance['annotationid']
  pprint(instance)
  r = requests.post(
      'https://vulcan.multicomp.cs.cmu.edu:9001/annotations/', data=instance, verify=False)

  # print(r.status_code)
  # print(r.text)
  # print("_"*10)
