import requests

# body = {'query':'rune'} # <-- use 'query' not `Search'
# response = requests.get('http://services.runescape.com/m=itemdb_rs/results#main-search', params=body)
# print (response.url)

# query = {'origin': 'Нью Йорк', 'destination': 'Стамбул', 'departDate': '10.12.2018', 'returnDate': '12.12.2018'}
# response = requests.get('https://www.aviasales.ru/', params=query)
# print (response.url)

# import mechanicalsoup
#
# # Connect to duckduckgo
# browser = mechanicalsoup.StatefulBrowser()
# browser.open('https://www.aviasales.ru/')
#
# # Fill-in the search form
# form = browser.select_form('form[name="userlogin"]')
# print(form)


import json
import re

def load_iata_db():
    with open('city_IATA.json') as f:
        city_iata = json.load(f)
    return city_iata

def get_city_code(city, db):
    if city in db:
        return db[city]
    else:
        return -1


def get_url(code1,code2, date1, date2 = None):
    base = 'https://www.aviasales.ru/search/'
    return base+code1+date1+code2+date2

def interpret_dates(str_containing_date):
    str_containing_date = str_containing_date.lower()
    str_containing_date = re.sub("\s\s+", " ", str_containing_date) #removes multiple spaces in a string
    months = {'января': 1, 'февраля': 2, 'марта':3}

    #matches two dates
    #template = r'(с\s)*(?P<date1>\d+.*?)\s?(по|-)\s?(?P<date2>\d+.*)'
    template = r'(с\s)*(?P<date1>\d+.*?)((\s?(по|-)\s?(?P<date2>\d+.*))|$)'
    m = re.match(template, str_containing_date)
    if m:
         print('date1:', m.group('date1'))
         print('date1:', m.group('date1'),' date2: ', m.group('date2'))
    else:
         print('NotFound')
    return
#
#interpret_dates('С 5 января 2018 по 8 марта')
#interpret_dates('5 января - 8 марта')
interpret_dates('5 января-8 марта')
interpret_dates('5.01-8.03')
#interpret_dates('5.01 по 8.03')

#interpret_dates('3-01-2017')
interpret_dates('5 сентября')

interpret_dates('5.01')