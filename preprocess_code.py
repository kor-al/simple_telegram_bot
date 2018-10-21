import json
from pprint import pprint
import re

"""
http://api.travelpayouts.com/data/ru/
Rearrange the response as {'city (ru)':'IATA code'}
"""

with open('cities.json', encoding='utf-8') as f:
    data = json.load(f)
#
result = {} #
for d in data:
    if d['name']:
        name = d['name'].lower()
        if '(' in name:
            alternative_name = name[name.find("(") + 1:name.find(")")]
            name = name[:name.find("(") - 1]
            result[alternative_name] = d['code']
        result[name] = d['code']
pprint(result)
print(len(result))
#
with open('city_IATA.json', 'w') as out:
     json.dump(result, out)