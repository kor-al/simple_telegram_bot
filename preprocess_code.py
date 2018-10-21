import json
from pprint import pprint

"""
Use API of https://iatacodes.org/ to get a json file of all IATA codes
Rearrange the response as {'country':'IATA code'}
"""

with open('cities.json') as f:
    data = json.load(f)

result = {} #
for d in data['response']:
    result[d['name']] = d['code']
pprint(result)
print(len(result))

with open('city_IATA.json', 'w') as out:
    json.dump(result, out)