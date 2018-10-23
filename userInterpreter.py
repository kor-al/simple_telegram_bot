import json
import re
import dateparser
import datetime

class ErrorIncorrectDate(ValueError):
    """Incorrect dates in terms of spelling"""
    def __init__(self, expr, msg):
        self.error_date = msg

    def get_date(self):
        return self.error_date

class ErrorCannotParseDate(ValueError):
    """Incorrect dates in terms of spelling"""
    def __init__(self, expr, msg):
        self.error_str = msg
    def get_date(self):
        return self.error_str

class ErrorNotYearAhead(ValueError):
    """Aviasales can suggest only for the year ahead."""
    def __init__(self, expr, msg):
        self.error_date = msg

    def get_date(self):
        return self.error_date

class ErrorDateSeq(ValueError):
    """A return date is earlier than a departure"""
    pass

class UserInterpreter:
    def __init__(self):
        self.city_iata = None
        self._initiate_aic_db()
        self._initiate_rus_months()
        self.base = 'https://www.aviasales.ru/search/'

    def _initiate_aic_db(self):
        with open('city_IATA.json') as f:
            self.city_iata = json.load(f)

    def _initiate_rus_months(self):
        self.months = {'December': 'декабря', 'January': 'января', 'February': 'февраля', 'March' : 'марта', 'April': 'апреля',
                       'May': 'мая', 'June': 'июня', 'July': 'июля', 'August': 'августа', 'September': 'сентября',
                       'October': 'октября', 'November': 'ноября'}

    def get_city_code(self, city):
        '''
        :param city: name of a city (RU)
        :return: IATA code if available
        '''
        city = city.lower()
        city = re.sub("озеро", "оз.", city)
        res = self.city_iata.get(city)
        if res:
            return res['code']
        else:
            return None

    def get_city_case(self, city, case = 'ro'):
        '''
        case ro = откуда?
        case vi = куда?
        :return: a city name modified according to a case
        '''
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
        '''
        url looks like https://www.aviasales.ru/search/MOW0705PAR08051 ,
        where MOW and PAR are IATA codes of departure and arrival cities
        0705 and 0805 are departure and return dates
        1 is for a '1-person' ticket
        :return: a url
        '''

        day_month = '{:02}{:02}'.format(date1.day, date1.month)
        res = self.base + code1 + day_month + code2
        if date2:
            return res + '{:02}{:02}'.format(date2.day, date2.month) + str(1)
        else:
            return res + str(1)

    def _is_in_one_year_window(self,date):
        # on the Aviasales website, dates must be
        # 1) less than a year away from NOW
        # 2) not in the past
        now = datetime.datetime.now()
        valid_now = lambda d:  now.date() <= d.date() <= now.replace(year=now.year + 1).date()
        if valid_now(date):
            return True
        else:
            return False

    def _interpret_one_date(self, date):
        missing_month = False
        if date is None:
            raise ErrorCannotParseDate('The date cannot be parsed', date)
        else:
            if date.isdigit(): #date is only one day: a user sent e.g. "8" or "32"
                # we would like to consider 8 as 8th of this month and year
                now = datetime.datetime.now()
                #we need to check if it is a valid day number for the current month
                try:
                    date_parsed = now.replace(day = int(date))
                except:
                    raise ErrorIncorrectDate('The date is incorrect', date)
                else: # the value is valid.
                    # it could be a final date or could be completed with the arrival date
                    missing_month = True
                    return date_parsed, missing_month
            else:
                date_parsed = dateparser.parse(date, settings={'DATE_ORDER': 'DMY', 'PREFER_DATES_FROM': 'future',
                                                      'PREFER_LANGUAGE_DATE_ORDER': False})
                if date_parsed:
                    if self._is_in_one_year_window(date_parsed):
                        return date_parsed, missing_month
                    else:
                        raise ErrorNotYearAhead('The date is not in the year from now', date_parsed)
                else:
                    raise ErrorCannotParseDate('The date is incorrect', date)

    def _complete_month_year(self, date1,date2):
        return date1.replace(year=date2.year, month = date2.month)


    def interpret_dates(self,str_containing_date):
        '''
        :param str_containing_date: string with two dates or only one (only departure)
        :return: parsed dates in the datetime format - but only only date not time
        '''

        str_containing_date = str_containing_date.lower()
        str_containing_date = re.sub("\s\s+", " ", str_containing_date)  # removes multiple spaces in a string

        template = r'(с\s)?(?P<date1>\d+.*?)((\s?(до|по|-)\s?(?P<date2>\d+.*))|$)'
        m = re.match(template, str_containing_date)
        if m:
            # print('date1:', m.group('date1'),' date2: ', m.group('date2'))
            date1, date2 = m.group('date1'), m.group('date2')

            #interpret date2 if present
            if date2:
                date2,_ = self._interpret_one_date(date2)

            date1, date1_missing_month = self._interpret_one_date(date1)

            if date2:
                if date1_missing_month:
                    date1 = self._complete_month_year(date1,date2) # true if 3-7 мая for example
                if date1 < date2:
                    return date1.date(), date2.date()
                else:
                    raise ErrorDateSeq('The order of dates is incorrect', date1, date2)
            else:
                return date1.date(), None
        else:
            raise ErrorCannotParseDate('The input is incorrect', str_containing_date)


    def convert_one_date_to_ru_str(self, date, use_year = False):
        """
        :param date: date in datetime format
        :return: returns date (day + month) in russian words, for example: 5.03 ==> 5 марта
        """
        date_str = '{dt.day} {dt:%B}'.format(dt=date).split(' ')
        if use_year:
            date_str = '{dt.day} {dt:%B} {dt.year}'.format(dt=date).split(' ')
        #date_str = date.strftime('%d %B').split(' ')
        date_str[1] = self.months[date_str[1]]
        return ' '.join(date_str)
