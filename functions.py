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
import dateparser
import datetime

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

def is_in_one_year_window(date):
    #dates must be less than a year away from NOW"""
    now = datetime.datetime.now().date()
    valid_now = lambda d: d.date()<=now<=d.replace(year = d.year + 1).date()
    if valid_now(date):
        return True
    else:
        return False

class IncorrectDates(ValueError):
   """incorrect dates"""
   pass

class NoSuggestion(ValueError):
   """cannot suggest any trips: dates must be less than a year away from NOW"""
   pass


def interpret_dates(str_containing_date):
    print('>>',str_containing_date)
    str_containing_date = str_containing_date.lower()
    str_containing_date = re.sub("\s\s+", " ", str_containing_date) #removes multiple spaces in a string
    onewaytrip = False

    template = r'(с\s)*(?P<date1>\d+.*?)((\s?(по|-)\s?(?P<date2>\d+.*))|$)'
    m = re.match(template, str_containing_date)
    if m:
         #print('date1:', m.group('date1'),' date2: ', m.group('date2'))
         date1, date2 = m.group('date1'),m.group('date2')

         if date1:
             date1 = dateparser.parse(date1)
         if date2:
             date2 = dateparser.parse(date2)
         else:
             onewaytrip = True

         if date1:
             if is_in_one_year_window(date1):
                 if onewaytrip:
                     print('<<<', date1.date(), None)
                     return date1.date(), None
                 elif date2:
                     if is_in_one_year_window(date2):
                         if date2>date1:
                             print('<<<', date1.date(), date2.date())
                             return date1.date(), date2.date()
                         else:
                             raise IncorrectDates('The order of dates is incorrect', date1, date2)
                     else:
                         raise NoSuggestion('The departure date is more than a year away', date2)
                 else:
                     raise IncorrectDates('The arrival date is incorrect', date2)
             else:
                 raise NoSuggestion('The arrival date is more than a year away', date1)
         else:
             raise IncorrectDates('The departure date is incorrect', date2)
    else:
        raise IncorrectDates('The input is incorrect', str_containing_date)


#
interpret_dates('С 5 января 2018 по 8 марта')
interpret_dates('5 января - 8 марта')
interpret_dates('5 января-8 марта')
#interpret_dates('8 марта - 5 января')
interpret_dates('8 марта - 5 января 2019')
interpret_dates('5.01-8.03')
interpret_dates('5.01 по 8.03')
interpret_dates('5 сентября')
interpret_dates('5.01')

interpret_dates('5.01 по блаблабла')
interpret_dates('блаблабла')

