import time
import calendar
import pytz
import datetime
from .CONSTANTS import MEAL_TO_PERIOD

# Default offset for Irvine from GMT (GMT-8 = -28800 seconds)
IRVINE_OFFSET = int(datetime.datetime.utcnow().astimezone(pytz.timezone('America/Los_Angeles')).utcoffset().total_seconds())

# Helper functions
def lower_first_letter(s: str) -> str:
    'Lowercase the first letter of a string'
    return s[0].lower() + s[1:]

def find_icon(icon_property: str, food_info: dict) -> bool:
    'Return true if the badge can be found in any of the dietary information images'
    return any(map(lambda diet_info: icon_property in diet_info["IconUrl"], food_info["DietaryInformation"]))

def normalize_time(time_struct: time.struct_time) -> int:
    'Formats the time into a 4-digit integer, controls how time is represented in API'
    return int(f'{time_struct.tm_hour}{time_struct.tm_min:02}')

def read_schedule_UTC(utc_time: str) -> int:
    '''
    Convert utc time string from UCI API to time.struct_time,
    convert struct to seconds since epoch, subtract 8 hours, and normalize to
    '''
    gmt_struct = time.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.0000000')
    local_struct = time.gmtime(calendar.timegm(gmt_struct) + IRVINE_OFFSET)
    return normalize_time(local_struct)


def get_irvine_time() -> time.struct_time:
    'Return the local time in normalized format'
    irvine_time = time.gmtime(time.time() + IRVINE_OFFSET)
    return irvine_time

def get_irvine_date() -> str:
    irvine_time = get_irvine_time()
    return time.strftime('%m/%d/%Y', irvine_time)

def get_current_meal():
    '''
    Return meal code for current time of the day
    Note: it does not consider open/closing; Breakfast begins at 12:00AM, and Dinner ends at 12:00AM
    '''
    irvine_time = get_irvine_time()
    now = normalize_time(irvine_time)

    breakfast   = 0000
    lunch       = 1100
    dinner      = 1630
    
    # After 16:30, Dinner, Meal-Code: 2
    if now >= dinner:
        return 2

    # After 11:00 Weekend, Brunch, Meal-Code: 3
    if now >= lunch and irvine_time.tm_wday >= 5:
        return 3

    # After 11:00 Weekday, Lunch, Meal-Code: 1
    if now >= lunch:
        return 1

    # After 00:00, Breakfast, Meal-Code: 0
    if now >= breakfast:
        return 0

def get_meal_name(schedule: dict, meal_id: int) -> str:
    if meal_id == 3 and 'brunch' not in schedule:
        return 'lunch'

    if meal_id == 1 and 'lunch' not in schedule:
        return 'brunch'
    
    return MEAL_TO_PERIOD[meal_id][1]
    
def parse_date(date: str) -> time.struct_time:
    '''
    Parse the date string "Weekday, Month Day, Year"
    into time.struct_time object
    '''
    return time.strptime(date, "%A, %B %d, %Y")

def normalize_time_from_str(time: str) -> int:
    '''
    Parse the string of time "int(:int) am/pm"
    in normalized format
    '''
    time = time.lower()
    pos1 = time.find('am')
    pm = False
    if(pos1 == -1):
        pos1 = time.find('pm')
        pm = True
    pos2 = time.find(':')
    
    if(pos2 == -1):
        inttime = int(time[0:pos1]) * 100
    else:
        inttime = int(time[0:pos2]) * 100 + int(time[pos2+1:pos1])
    if(inttime >= 1200 and inttime < 1300):
        if(not pm):
            inttime -= 1200
        else:
            return inttime
    if(pm):
        inttime += 1200
    return inttime

def get_date_str(t: time.struct_time) -> str:
    return time.strftime('%m/%d/%Y', t)