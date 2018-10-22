import json
import re
import dateparser
import datetime


class ErrorIncorrectDates(ValueError):
    """incorrect dates"""
    pass

class ErrorIncorrectName(ValueError):
    """incorrect name"""
    pass

class ErrorNoSuggestion(ValueError):
    """cannot suggest any trips: dates must be less than a year away from NOW"""
    pass

class UserInterpretator:
    def __init__(self):
        self.city_iata = None
        self._initiate_aic_db()
        self._initiate_rus_months()
        self.base = 'https://www.aviasales.ru/search/'

    def _initiate_aic_db(self):
        with open('city_IATA.json') as f:
                self.city_iata = json.load(f)

    def _initiate_rus_months(self):
        self.months = {'December': 'Декабря', 'January': 'Января', 'February': 'Февраля', 'March' : 'Марта', 'April': 'Апреля',
                  'May': 'Мая', 'June': 'Июня', 'July': 'Июля', 'August': 'Августа', 'September': 'Сентября',
                  'October': 'Октября', 'November': 'Ноября'}

    def get_city_code(self, city):
        city = city.lower()
        city = re.sub("озеро", "оз.", city)
        res = self.city_iata.get(city)
        if res:
            return res['code']
        else:
            return None

    def get_city_case(self, city, case = 'ro'):
        # case ro = откуда?
        # case vi = куда?
        city = city.lower()
        cases =  self.city_iata.get(city)['cases']
        if case in cases:
            return cases[case]
        elif case == 'vi':
            return 'в' + city.capitalize()
        else:
            #return nominative
            return city
        #
    def get_url(self,code1, code2, date1, date2=None):
        day_month = '{:02}{:02}'.format(date1.day, date1.month)
        res = self.base + code1 + day_month + code2
        if date2:
                return res + '{:02}{:02}'.format(date2.day, date2.month) + str(1)
        else:
                return res + str(1)

    def _is_in_one_year_window(self,date):
        # dates must be less than a year away from NOW"""
        now = datetime.datetime.now()
        valid_now = lambda d:  now.date() <= d.date() <= now.replace(year=now.year + 1).date()
        if valid_now(date):
            return True
        else:
            return False

    def parse_name(self,name):
        if re.match("^[ A-Za-z0-9_-]*$", name):
            return name
        else:
            raise ErrorIncorrectName('Incorrect name',name)


    def interpret_dates(self,str_containing_date):
        str_containing_date = str_containing_date.lower()
        date1, date2 = None, None
        str_containing_date = re.sub("\s\s+", " ", str_containing_date)  # removes multiple spaces in a string
        onewaytrip = False

        template = r'(с\s)*(?P<date1>\d+.*?)((\s?(по|-)\s?(?P<date2>\d+.*))|$)'
        m = re.match(template, str_containing_date)
        if m:
            # print('date1:', m.group('date1'),' date2: ', m.group('date2'))
            date1, date2 = m.group('date1'), m.group('date2')

            if date1:
                date1 = dateparser.parse(date1, settings={'DATE_ORDER': 'DMY','PREFER_DATES_FROM': 'future'})
            if date2:
                date2 = dateparser.parse(date2, settings={'DATE_ORDER': 'DMY'})
            else:
                onewaytrip = True

            if date1:
                if self._is_in_one_year_window(date1):
                    if onewaytrip:
                        #print('<<<', date1.date(), None)
                        return date1.date(), None
                    elif date2:
                        if self._is_in_one_year_window(date2):
                            if date2 > date1:
                                #print('<<<', date1.date(), date2.date())
                                return date1.date(), date2.date()
                            else:
                                raise ErrorIncorrectDates('The order of dates is incorrect', date1, date2)
                        else:
                            raise ErrorNoSuggestion('The departure date is more than a year away', date2)
                    else:
                        raise ErrorIncorrectDates('The arrival date is incorrect', date2)
                else:
                    raise ErrorNoSuggestion('The arrival date is more than a year away', date1)
            else:
                raise ErrorIncorrectDates('The departure date is incorrect', date2)
        else:
            raise ErrorIncorrectDates('The input is incorrect', str_containing_date)


    def convert_one_date_to_ru_str(self, date):
        date_str = '{dt.day} {dt:%B}'.format(dt=date).split(' ')
        #date_str = date.strftime('%d %B').split(' ')
        date_str[1] = self.months[date_str[1]]
        return ' '.join(date_str)
