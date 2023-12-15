import traceback
from collections import defaultdict
import time

from .util import read_schedule_UTC, get_current_meal, get_meal_name, get_irvine_date, get_name, NUTRITION_PROPERTIES, DEFAULT_PRICES, EMPTY_MENU_OBJECT, MENU_DATA_ERROR_OBJECT

from .campusdish_interface import get_menu_data, get_schedule_data, get_themed_event_data

from .sorting import station_ordering_key


def _lower_first_letter(s: str) -> str:
    'Lowercase the first letter of a string'
    return s[0].lower() + s[1:]


def _get_menu(location, meal_id, date):
    '''
    Gets the menu (list of stations, each of which contains multiple dishes) for a given dining hall, meal, and date.
    '''

    def _find_icon(icon_property: str, food_info: dict) -> bool:
        'Return true if the badge can be found in any of the dietary information images'
        return any(map(lambda diet_info: icon_property in diet_info["IconUrl"], food_info["DietaryInformation"]))

    station_dict = defaultdict(lambda: defaultdict(lambda: []))

    try:
        menu_data = get_menu_data(location, meal_id, date)

        station_id_to_name = dict(
            [(entry['StationId'], entry['Name']) for entry in menu_data["MenuStations"]])
        dish_list = menu_data["MenuProducts"]

        for dish in dish_list:
            details = dish['Product']
            station_name = station_id_to_name[dish['StationId']].replace(
                '/ ', ' / ')
            category_name = details['Categories'][0]['DisplayName']

            dish_object = {
                'name': details['MarketingName'],
                'description': details['ShortDescription'],
                'nutrition': dict([(_lower_first_letter(property_name), details.get(property_name)) for property_name in NUTRITION_PROPERTIES]) |
                {
                    'isEatWell': _find_icon('EatWell', details),
                    'isPlantForward': _find_icon('PlantForward', details),
                    'isWholeGrain': _find_icon('WholeGrain', details),
                },
            }

            station_dict[station_name][category_name].append(dish_object)

        menu = []

        # iterate over station names in custom order
        for station_name in sorted(station_dict, key=station_ordering_key):
            menu.append(
                {
                    'station': station_name,
                    'menu': [{'category': category, 'items': items} for category, items in station_dict[station_name].items()]
                }
            )
        return menu or EMPTY_MENU_OBJECT
    except:
        traceback.print_exc()
        return MENU_DATA_ERROR_OBJECT


def make_response_body(location: str, meal_id: int = None, date: str = None) -> dict:
    ''' 
    Makes the dict with all the details in the response. 

    Needs to match this enum on the iOS client: https://github.com/shengyuan-lu/ZotMeal-iOS/blob/main/ZotMeal/Data%20Structure/Restaurant.swift#L21-L30

    Permalink in case it gets moved (but then the requirements might've changed): https://github.com/shengyuan-lu/ZotMeal-iOS/blob/e8585b56f6591ed2d7cd1715a494659b09cc5167/ZotMeal/Data%20Structure/Restaurant.swift#L21-L30 
    '''

    if meal_id is None:
        meal_id = get_current_meal()

    restaurant = get_name(location)
    schedule = get_schedule_data(restaurant)

    date = date or get_irvine_date()
    return {
        'date': date,
        'restaurant': restaurant,
        'refreshTime': int(time.time()),
        'schedule': schedule,
        'currentMeal': get_meal_name(schedule, meal_id),
        'price': DEFAULT_PRICES,
        'themed': get_themed_event_data(restaurant),
        'all': _get_menu(location, meal_id, date)
    }
