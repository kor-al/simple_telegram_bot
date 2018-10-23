import json
import re
import dateparser
import datetime

class ErrorIncorrectDates(ValueError):
    """Incorrect dates in terms of spelling"""
    pass

class ErrorNotYearAhead(ValueError):
    """Aviasales can suggest only for the year ahead."""
    pass

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
        # on the Aviasales website, dates must be less than a year away from NOW
        now = datetime.datetime.now()
        valid_now = lambda d:  now.date() <= d.date() <= now.replace(year=now.year + 1).date()
        if valid_now(date):
            return True
        else:
            return False


    def interpret_dates(self,str_containing_date):
        '''
        :param str_containing_date: string with two dates or only one (only departure)
        :return: parsed dates in the datetime format - but only only date not time
        '''

        str_containing_date = str_containing_date.lower()
        str_containing_date = re.sub("\s\s+", " ", str_containing_date)  # removes multiple spaces in a string
        onewaytrip = False

        template = r'(с\s)?(?P<date1>\d+.*?)((\s?(до|по|-)\s?(?P<date2>\d+.*))|$)'
        m = re.match(template, str_containing_date)
        if m:
            # print('date1:', m.group('date1'),' date2: ', m.group('date2'))
            date1, date2 = m.group('date1'), m.group('date2')

            if date1:
                date1 = dateparser.parse(date1, settings={'DATE_ORDER': 'DMY','PREFER_DATES_FROM': 'future'})
            if date2:
                date2 = dateparser.parse(date2, settings={'DATE_ORDER': 'DMY','PREFER_DATES_FROM': 'future'})
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
                                raise ErrorDateSeq('The order of dates is incorrect', date1, date2)
                        else:
                            raise ErrorNotYearAhead('The arrival date is not in the year from now', date2)
                    else:
                        raise ErrorIncorrectDates('The arrival date is incorrect', date2)
                else:
                    raise ErrorNotYearAhead('The arrival date is not in the year from now', date1)
            else:
                raise ErrorIncorrectDates('The departure date is incorrect', date2)
        else:
            raise ErrorIncorrectDates('The input is incorrect', str_containing_date)


    def convert_one_date_to_ru_str(self, date):
        """
        :param date: date in datetime format
        :return: returns date (day + month) in russian words, for example: 5.03 ==> 5 марта
        """
        date_str = '{dt.day} {dt:%B}'.format(dt=date).split(' ')
        #date_str = date.strftime('%d %B').split(' ')
        date_str[1] = self.months[date_str[1]]
        return ' '.join(date_str)
