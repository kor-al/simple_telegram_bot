import json
from pprint import pprint
import re

"""
http://api.travelpayouts.com/data/ru/
Rearrange the response as {'city (ru)':{ code = 'IATA code', cases = {cases}, country = 'country_code' }
"""

with open('cities.json', encoding='utf-8') as f:
    data = json.load(f)

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
Problem: there are cities with the same names but in different countries. 
Solution for now: take only one of them. If there N cities with the same name and some of them are in the US and
others are elsewhere, prefer the second group and choose the first city-country pair among them.
(Reason: there are too many cities with european names in the US while they are not that popular in terms of travelling)
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

with open('city_IATA.json', 'w') as out:
      json.dump(filtered_result, out)