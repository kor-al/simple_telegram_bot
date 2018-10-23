import json
import requests
from pprint import pprint
import re

"""
http://api.travelpayouts.com/data/ru/
Rearrange the response as {'city (ru)':{ code = 'IATA code', cases = {cases}, country = 'country_code' }
"""

content = requests.get("http://api.travelpayouts.com/data/ru/cities.json")
data = json.loads(content.content)

"""
First: explore the data in terms of names of cities and their codes. 
Save all the cities with the same name in a corresponding list in the resulting dictionary
result = {name : [cities with the same name but different IATA codes]}
"""

result = {} #
for d in data:
    if d['name']:
        name = d['name'].lower()
        if '(' in name:
            alternative_name = name[name.find("(") + 1:name.find(")")]
            name = name[:name.find("(") - 1]
            result[alternative_name] = [dict(code = d['code'], cases = {}, country = d['country_code'])]
        if name in result:
            result[name].append(dict(code = d['code'], cases = d['cases'], country = d['country_code']))
        else:
            result[name]= [dict(code = d['code'], cases = d['cases'], country = d['country_code'])]

'''
Problem: there are cities with the same name but in different countries. 
Solution for now: take only one of them. Prefer european cities to their american duplicates as they are more likely to have airports
'''

filtered_result = {}
count_cities_the_same_name = 0
for n in result:
    if len(result[n])>1:
        count_cities_the_same_name+=1
        countries = [c['country'] for c in result[n]]
        if len(set(countries)) == 1:
            filtered_result[n] = result[n][0]
        else:
            is_US = [c == 'US' for c in countries]
            ind = is_US.index(False)
            #print(n, countries )
            filtered_result[n] = result[n][ind] # any of countries that are not us
    else:
        filtered_result[n] = result[n][0]

print('Cities with the same name:', count_cities_the_same_name)
#
print(filtered_result['москва'])
print(filtered_result['лондон'])

# with open('city_IATA.json', 'w') as out:
#       json.dump(filtered_result, out)