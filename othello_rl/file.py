import json
import re

def parse_ql_json(path, scale = 1):
  with open(path, 'r') as f:
    data_dict = json.load(f)
  
  new_dict = {}
  p = re.compile(r'([0-9]+)\, ([0-9]+)')
  for k, v in data_dict.items():
    t = p.match(k[1:-1])
    t = t.groups()
    t = (int(t[0]), int(t[1]))
    new_dict[t] = v*scale

  return new_dict