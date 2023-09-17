import datetime
from typing import Optional
from thompcoUtils import config_utils
from thompcoUtils.log_utils import get_logger
import holidays


def month_name_to_number(month_name):
    """
    Converts a month name to an integer
    param month_name: the name of the month to convert
    return: the month of the year as a 1-based integer
    """
    try:
        dt = datetime.datetime.strptime(month_name, "%B")
    except ValueError:
        dt = datetime.datetime.strptime(month_name, "%b")
    month_number = dt.month
    return month_number


def month_number_to_name(month_number):
    """
    Converts a month number (1-12) to a month name (January - December)
    param month_number: the number of the month to convert
    return: the name of the month
    """
    date = datetime.datetime(month=month_number, day=1, year=1)
    return date.strftime("%B")


class PeakTimes:
    """
    Class to manage peak times for power generation/consumption.  It constructs from a ConfigManager
    """

    def __init__(self, config_mgr: Optional['config_utils.ConfigManager'], section='peak_time'):
        """
        Initializes a PeakTimes from a configuration file

        Here is an example:
        [peak_time]
        [peak_time.seasons]
        names = ['summer', 'winter']

        [peak_time.summer]
        peaks = 2
        start_month = October
        end_month = March
        start1 = 06:00:00
        end1 = 10:00:00
        start2 = 18:00:00
        end2 = 20:00:00

        [peak_time.winter]
        peaks = 1
        start_month = April
        end_month = Sep
        start1 = 12:00:00
        end1 = 21:00:00

        param config_mgr: the configuration manager
        param section: the section the peak times are in
        """

        header = section + '.allowed'
        self.allowed_holidays = self.allowed_holidays = config_mgr.read_entry(
            header, 'names', ["Thanksgiving", "New Year's Day", "Christmas Day", "Christmas Day (Observed)",
                              "Memorial Day", "Independence Day", "Labor Day"])
        header = section + '.seasons'
        self.peak_seasons = {}
        season_names = config_mgr.read_entry(header, 'names', [])
        self.weekends_off_peak = config_mgr.read_entry(header, 'weekends_off_peak', False)
        self.holidays_off_peak = config_mgr.read_entry(header, 'holidays_off_peak', False)
        self.holidays = holidays.US()

        for peak_time in season_names:
            header = section + '.' + peak_time
            count = config_mgr.read_entry(header, 'count', 1)
            start_month = month_name_to_number(config_mgr.read_entry(header, 'start_month', 'January'))
            end_month = month_name_to_number(config_mgr.read_entry(header, 'end_month', 'January'))
            times = []
            blank_time = datetime.time(hour=0, minute=0, second=0)

            for i in range(1, count + 1):
                t = {'start': config_mgr.read_entry(header, 'start{}'.format(i), blank_time),
                     'end': config_mgr.read_entry(header, 'end{}'.format(i), blank_time)}
                times.append(t)
            self.peak_seasons[peak_time] = {}
            self.peak_seasons[peak_time]['times'] = times
            self.peak_seasons[peak_time]['start_month'] = start_month
            self.peak_seasons[peak_time]['end_month'] = end_month

    def __str__(self):
        """
        returns this object as a string
        return: a string representing this object
        """
        rtn = 'weekends off-peak:{}, holidays off-peak:{}'.format(self.weekends_off_peak, self.holidays_off_peak)

        for peak_season in self.peak_seasons:
            rtn += ';'
            rtn += '{}-{}: '.format(month_number_to_name(self.peak_seasons[peak_season]['start_month']),
                                    month_number_to_name(self.peak_seasons[peak_season]['end_month']))
            r = ''
            for time in self.peak_seasons[peak_season]['times']:
                if r != '':
                    r += '+'
                r += '{}-{}'.format(time['start'],
                                    time['end'])
            rtn += r
        recognized_holidays = ', '.join(self.allowed_holidays)
        rtn += ";Recognized Holidays:" + recognized_holidays
        return rtn

    def pretty_print(self):
        """
        returns the object as a pretty string with carriage returns for visibility
        return: a string representing this object
        """
        rtn = str(self)
        rtn = rtn.replace(': ', ':\n')
        rtn = rtn.replace('+', '\n')
        rtn = rtn.replace(';', '\n')
        return rtn

    def season_start_month(self, season):
        """
        The start month of the season
        param season: the season to get the start month of
        returns: the name of the month the season starts
        """
        return month_number_to_name(self.peak_seasons[season]['start_month'])

    def season_end_month(self, season):
        """
        The end month of the season
        param season: the season to get the end month of
        returns: the name of the month the season ends
        """
        return month_number_to_name(self.peak_seasons[season]['end_month'])

    def month_range(self, season):
        """
        Gets the range of the specified season
        param season: the season to test with
        returns: a string representing the month-range of the season
        """
        if season in self.peak_seasons:
            return '{} - {}'.format(month_number_to_name(self.peak_seasons[season]['start_month']),
                                    month_number_to_name(self.peak_seasons[season]['end_month']))
        return ''

    def time_range(self, season):
        """
        Gets the time range of the specified season
        param season: the required season
        returns: a string representing the time-range(s) of the season
        """
        rtn = ''
        if season in self.peak_seasons:
            for time_range in self.peak_seasons[season]['times']:
                if rtn != '':
                    rtn += ', '
                rtn += '{} - {}'.format(time_range['start'], time_range['end'])
        return rtn

    def get_peak_times(self, start_date: Optional['datetime.date'], end_date: Optional['datetime.date'] = None):
        """
        Returns the start and end times for a date.  If dt is None, today is used
        :param start_date: start date to get peak times for
        :param end_date: end date to get peak times for
        :return: start and end times peak times for today.
        """
        logger = get_logger()
        season_info = []
        dt = datetime.datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=0)

        if end_date is None:
            end_date = start_date

        ed = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=23)

        while True:
            in_peak = False
            weekend = False
            holiday = False

            if self.weekends_off_peak and dt.weekday() > 4:
                weekend = True
                logger.debug('Weekends are off-peak and we are on either Saturday or Sunday')
            elif dt in self.allowed_holidays:
                holiday = True
                logger.debug('Holidays are off-peak and we are on a holiday ({})'.format(datetime.datetime.now()))
            info = {'name': None, 'times': []}

            for season in self.peak_seasons:
                in_season = False
                s = self.peak_seasons[season]

                if s['start_month'] < s['end_month']:  # both months are in the same year
                    if s['start_month'] <= dt.month <= s['end_month']:
                        in_season = True
                elif dt.month >= s['start_month'] or dt.month <= s['end_month']:
                    in_season = True

                if in_season:
                    info['name'] = season
                    info['start_month'] = s['start_month']
                    info['end_month'] = s['end_month']

                    for t in s['times']:
                        if (t['start'] < dt.time() < t['end']) and not in_peak:
                            in_peak = True
                        info['times'].append({'start': t['start'], 'end': t['end']})
                    break

            info['in_holiday'] = holiday
            info['in_weekend'] = weekend
            info['in_peak'] = not holiday and not weekend
            info['date'] = dt.date()
            season_info.append(info)
            dt += datetime.timedelta(days=1)

            if dt > ed:
                break
        return season_info

    def in_peak(self, dt: Optional['datetime'] = None):
        """
        Calculates if the specified time is in-peak
        param dt: the datetime to compare
        True, season, details
        False, None, details
        return: tuple of: true if the specified datetime is a peak-time, false if not, season, and reason
        """
        logger = get_logger()
        if dt is None:
            dt = datetime.datetime.now()
        today_str = '{:02d}-{:02d}-{}'.format(dt.month, dt.day, dt.year)
        weekend = False
        holiday = False
        all_holidays = holidays.country_holidays('US', subdiv='FL')
        today = all_holidays.get(dt)

        # if weekends are off-peak, see if today is a weekend
        if self.weekends_off_peak and dt.weekday() > 4:
            logger.debug('Weekends are off-peak and we are on either Saturday or Sunday')
            weekend = True

        # if holidays are off-peak, see if today is a holiday
        if self.holidays_off_peak and today_str in self.holidays and today in self.allowed_holidays:
            logger.debug('Holidays are off-peak and we are on a holiday ({})'.format(today))
            holiday = True

        # first find the correct peak time
        dt_month = dt.month

        for peak_season in self.peak_seasons:
            in_season = False
            start_month = self.peak_seasons[peak_season]['start_month']
            end_month = self.peak_seasons[peak_season]['end_month']

            if start_month < end_month:
                logger.debug('start month and end month are in the same year')
                # start and end are in the same year:
                # apr < dt_month < june
                if start_month <= dt_month <= end_month:
                    logger.debug('we are currently in {} season'.format(peak_season))
                    in_season = True
            else:
                logger.debug('start month is in one year and end month is in the next year')
                # start is in one year, end is in the next:
                # oct < dt_month or dt_month < feb:
                if start_month <= dt_month or dt_month <= end_month:
                    logger.debug('we are currently in {} season'.format(peak_season))
                    in_season = True

            if in_season:
                times = ''
                for t in self.peak_seasons[peak_season]['times']:
                    if times != '':
                        times += ','
                    times = '{}{}-{}'.format(times, t['start'], t['end'])
                if weekend:
                    logger.debug('returning false because in weekend')
                    return False, peak_season, 'weekend ({})'.format(dt.strftime('%A'))
                if holiday:
                    logger.debug('returning false because in holiday')
                    return False, peak_season, 'holiday ({})'.format(self.holidays.get(today_str))
                # this is the correct season, now check the times
                for time in self.peak_seasons[peak_season]['times']:
                    if time['start'] <= dt.time() < time['end']:
                        logger.debug('returning true because between {}'.format(times))
                        return True, peak_season, 'between {}'.format(times)
                logger.debug('returning false because outside of {}'.format(times))
                return False, peak_season, 'outside of {}'.format(times)
        raise RuntimeError('{} not accounted for in given seasons'.format(dt))

    def validate(self):
        year = datetime.datetime.now().year

        for month in range(1, 12):
            for hour in range(0, 23):
                for minute in range(0, 60):
                    dt = datetime.datetime(year=year, month=month, day=1, hour=hour, minute=minute, second=0)
                    try:
                        self.in_peak(dt)
                    except RuntimeError as e:
                        print(e)
                        return False
        return True
