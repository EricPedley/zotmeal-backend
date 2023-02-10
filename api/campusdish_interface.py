import traceback
import requests
import bs4
import re
from bs4 import BeautifulSoup as bs
from .util import normalize_time_from_str, parse_date, get_irvine_time, get_date_str, MEAL_TO_PERIOD, EVENTS_PLACEHOLDER, LOCATION_INFO


def get_menu_data(location, meal_id, date):
    '''
    Given a valid location, meal_id, and date,
    perform get request for the diner_json and return the dict at diner_json['Menu']
    '''
    location_id = LOCATION_INFO[location]['id']

    response = requests.get(
        f'https://uci.campusdish.com/api/menu/GetMenus?locationId={location_id}&periodId={MEAL_TO_PERIOD[meal_id][0]}&date={date}'
    )
    if response.status_code == 200:
        payload = response.json()
        if 'Menu' in payload:
            return payload['Menu']
        else:
            raise KeyError(
                f'Key "Menu" not found in campusdish response object. Response payload below:\n{payload}')
    else:
        print("Response error message: ", response.json())
        response.raise_for_status()


def get_schedule_data(restaurant: str) -> dict:
    '''
    Given the restaurant name,
    perform get request, then parse the HTML code using BeautifulSoup 4
    return a dictionary
    schedule time use int because frontend work with int
    schedule time is (100*hours)+minutes, where hours is in 24-hour time
    '''
    # hardcoded schedule (replace with actual schedule when bug is fixed)
    day_of_week = get_irvine_time().tm_wday # 0-6 inclusive, 0=monday
    schedule = {
        "breakfast": {
            "start": 715,
            "end": 1100
        },
        "lunch": {
            "start":1100,
            "end":1630
        },
        "dinner": {
            "start": 1630,
            "end": 2300
        }
    }
    if day_of_week >= 4: # if friday or later
        schedule["dinner"]["end"] = 2000
        if day_of_week >= 5: # if it's the weekend
            schedule["brunch"] = schedule["lunch"]
            del schedule["lunch"]
    return schedule


    url = 'https://uci.campusdish.com/LocationsAndMenus/'
    if restaurant == 'Anteatery':
        url += 'TheAnteatery'
    else:
        url += restaurant
    schedule = {}
    soup = bs(requests.get(url).text, 'html.parser')
    meal_period = soup.select('.mealPeriod')[:5]
    location_times = soup.select('span[class=location__times]')[:5]
    for idx, meal in enumerate(meal_period):
        meal = meal.getText().lower()
        times = location_times[idx].getText().split(' - ')
        if re.match(r"^\d?\d:\d\d(AM|PM)$", times[0]) and re.match(r"^\d?\d:\d\d(AM|PM)$", times[1]):
            start = normalize_time_from_str(times[0])
            end = normalize_time_from_str(times[1])
            schedule[meal] = {"start": start, "end": end}
        else:
            print("Invalid time")
            schedule = {
                "breakfast": {
                    "start": 0,
                    "end": 1
                },
                "lunch": {
                    "start": 2,
                    "end": 3
                },
                "dinner": {
                    "start": 4,
                    "end": 5
                }
            }
    return schedule


def get_themed_event_data(restaurant: str) -> list[dict]:
    '''
    Given a valid restaurant name,
    perform get request, then parse the HTML code for the event_json using BeautifulSoup 4
    '''
    url = 'https://uci.campusdish.com/LocationsAndMenus/'
    if restaurant == 'Anteatery':
        url += 'TheAnteatery'
    else:
        url += restaurant

    try:
        soup = bs(requests.get(url).text, 'html.parser')
        table_rows = soup.find_all('tr', attrs={"style": "height: 10pt;"})

        def event_from_soup(soup_object: bs4.element.Tag):
            text_list = [td.getText().strip()
                         for td in soup_object.find_all("td")]
            try:
                if text_list[0] == '':
                    return False
                event_date = parse_date(text_list[0])
                if event_date < get_irvine_time():
                    return False

                # Warning: this is a weird character. The character U+2013 "–" could be confused with the character U+002d "-", which is more common in source code. UCI uses this weird character in their website for some reason, but if they change it to a normal hyphen this will break.
                start_time, end_time = map(
                    normalize_time_from_str, text_list[3].split(' – '))
                return {
                    'date': get_date_str(event_date),
                    'name': text_list[1],
                    'service_start': start_time,
                    'service_end': end_time
                }
            except Exception as e:
                traceback.print_exc()
        return list(filter(None, (event_from_soup(row) for row in table_rows)))
    except:
        return EVENTS_PLACEHOLDER
