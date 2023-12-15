import time
import calendar
import pytz
import datetime
from dataclasses import dataclass
from typing import Dict, List

# type definitions.
# These should match the types in the iOS source code: https://github.com/shengyuan-lu/ZotMeal-iOS/tree/main/ZotMeal/Data%20Structure


@dataclass
class Schedule:
    todo: None


@dataclass
class MenuItem:
    name: str
    description: str
    nutrition: dict


@dataclass
class Category:
    category: str
    items: List[MenuItem]


@dataclass
class Station:
    station: str
    menu: List[Category]


@dataclass
class APIResponse:
    date: str
    restaurant: str
    refreshTime: int
    schedule: Schedule
    currentMeal: str
    price: Dict[str, int]
    themed: list
    all: List[Station]


# Helper functions

def is_valid_location(location: str) -> bool:
    'Check if the location is valid'
    if location in LOCATION_INFO:
        return True
    return False


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

    breakfast = 0000
    lunch = 1100
    dinner = 1630

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

    if schedule:
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
    # if len(date) > 0:
    return time.strptime(date, "%B %d, %Y")


def normalize_time_from_str(time: str) -> int:
    '''
    Parse the string of time "int(:int) am/pm"
    in normalized format
    '''
    time = time.lower()
    pos1 = time.find('am')
    pm = False
    if (pos1 == -1):
        pos1 = time.find('pm')
        pm = True
    pos2 = time.find(':')

    if (pos2 == -1):
        inttime = int(time[0:pos1]) * 100
    else:
        inttime = int(time[0:pos2]) * 100 + int(time[pos2+1:pos1])
    if (inttime >= 1200 and inttime < 1300):
        if (not pm):
            inttime -= 1200
        else:
            return inttime
    if (pm):
        inttime += 1200
    return inttime


def get_date_str(t: time.struct_time) -> str:
    return time.strftime('%m/%d/%Y', t)


def get_name(location: str):
    'Returns the location name, except capitalized, using a dictionary lookup'
    return LOCATION_INFO[location]['official']


def get_id(location: str) -> int:
    'Returns the id campusdish uses for the location'
    return LOCATION_INFO[location]['id']


# Default offset for Irvine from GMT (GMT-8 = -28800 seconds)
IRVINE_OFFSET = int(datetime.datetime.utcnow().astimezone(
    pytz.timezone('America/Los_Angeles')).utcoffset().total_seconds())
# Constants

LOCATION_INFO = {
    'brandywine': {
        'official': 'Brandywine',
        'id': 3314,
    },

    'anteatery': {
        'official': 'Anteatery',
        'id': 3056,
    }
}

DEFAULT_PRICES = {
    'breakfast': 9.75,
    'lunch': 13.75,
    'brunch': 13.75,
    'dinner': 14.95
}

# Default opening and closing times
# TODO: Might implement a class to determine default open/close depending on day
DEFAULT_OPEN = 715
DEFAULT_CLOSE = 2200


# Relevant Nutrition Properties
NUTRITION_PROPERTIES = (
    'IsVegan',
    'IsVegetarian',
    'ServingSize',
    'ServingUnit',
    'Calories',
    'CaloriesFromFat',
    'TotalFat',
    'TransFat',
    'Cholesterol',
    'Sodium',
    'TotalCarbohydrates',
    'DietaryFiber',
    'Sugars',
    'Protein',
    'VitaminA',
    'VitaminC',
    'Calcium',
    'Iron',
    'SaturatedFat'
)

# MEAL ID > (PERIOD ID, MEAL NAME)
# meals can be referred to by their id or period id alias
# TODO: there might be a better way to implement this
MEAL_TO_PERIOD = {
    0: (49, 'breakfast'),
    1: (106, 'lunch'),
    2: (107, 'dinner'),
    3: (2651, 'brunch')
}

EVENTS_PLACEHOLDER = [
    {
        "date": "04/20/2069",
                "name": "placeholder",
                "service_start": 1100,
                "service_end": 2200
    }
]

EMPTY_MENU_OBJECT = [
    {
        'station': 'Error',
        'menu': [
            {
                'category': 'Error Description',
                            'items': [{
                                'name': 'The menu is empty for today',
                                'description': '😭',
                                "nutrition": {
                                    "isVegan": True,
                                    "isVegetarian": True,
                                    "servingSize": "2",
                                    "servingUnit": "tablespoons",
                                    "calories": "60",
                                    "caloriesFromFat": "45",
                                    "totalFat": "5",
                                    "transFat": "0",
                                    "cholesterol": "0",
                                    "sodium": "200",
                                    "totalCarbohydrates": "4",
                                    "dietaryFiber": "0",
                                    "sugars": "4",
                                    "protein": "0",
                                    "vitaminA": None,
                                    "vitaminC": None,
                                    "calcium": None,
                                    "iron": None,
                                    "saturatedFat": "0.5",
                                    "isEatWell": False,
                                    "isPlantForward": False,
                                    "isWholeGrains": False
                                }
                            }]
            }
        ]
    }
]

MENU_DATA_ERROR_OBJECT = [
    {
        'station': 'Error',
        'menu': [
            {
                'category': 'Error Description',
                            'items': [{
                                'name': 'We encountered an error getting the menu data. If the campusdish website has the menu but we don\'t, send me an email at katyh1@uci.edu and I\'ll look into a fix.',
                                'description': '🤷‍♂️',
                                "nutrition": {
                                    "isVegan": True,
                                    "isVegetarian": True,
                                    "servingSize": "2",
                                    "servingUnit": "tablespoons",
                                    "calories": "60",
                                    "caloriesFromFat": "45",
                                    "totalFat": "5",
                                    "transFat": "0",
                                    "cholesterol": "0",
                                    "sodium": "200",
                                    "totalCarbohydrates": "4",
                                    "dietaryFiber": "0",
                                    "sugars": "4",
                                    "protein": "0",
                                    "vitaminA": None,
                                    "vitaminC": None,
                                    "calcium": None,
                                    "iron": None,
                                    "saturatedFat": "0.5",
                                    "isEatWell": False,
                                    "isPlantForward": False,
                                    "isWholeGrains": False
                                }
                            }]
            }
        ]
    }
]


# anteatery 01/14/2022 breakfast
# https://uci.campusdish.com/api/menu/GetMenus?locationId=3056&date=01/14/2022&periodId=49

# brandywine lunch 10/14/2021: https://uci.campusdish.com/en/LocationsAndMenus/Brandywine?locationId=3314&storeIds=&mode=Daily&periodId=106&date=10%2F14%2F2021
# anteatery examples:
# example url with query (10/14/2021 lunch): https://uci.campusdish.com/en/LocationsAndMenus/TheAnteatery?locationId=3056&storeIds=&mode=Daily&periodId=106&date=10%2F14%2F2021
# example 2 (10/14/2021 dinner): https://uci.campusdish.com/en/LocationsAndMenus/TheAnteatery?locationId=3056&storeIds=&mode=Daily&periodId=107&date=10%2F14%2F2021
# (10/15/2021 dinner): https://uci.campusdish.com/en/LocationsAndMenus/TheAnteatery?locationId=3056&storeIds=&mode=Daily&periodId=107&date=10%2F15%2F2021
# (10/21/2021 breakfast): https://uci.campusdish.com/en/LocationsAndMenus/TheAnteatery?locationId=3056&storeIds=&mode=Daily&periodId=105&date=10%2F21%2F2021
