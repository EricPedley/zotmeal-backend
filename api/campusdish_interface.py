import traceback
import requests
import bs4
import re
from datetime import datetime
from bs4 import BeautifulSoup as bs
from .util import normalize_time_from_str, parse_date, get_irvine_time, get_date_str, MEAL_TO_PERIOD, EVENTS_PLACEHOLDER, LOCATION_INFO

def get_menu_data(location, meal_id, date):
    '''
    Given a valid location, meal_id, and date,
    perform get request for the diner_json and return the dict at diner_json['Menu']
    '''
    location_id = LOCATION_INFO[location]['id']


    response = requests.get(
        f'https://uci.campusdish.com/api/menu/GetMenus?locationId={location_id}&periodId={MEAL_TO_PERIOD[meal_id][0]}&date={date}',
        headers={'USER-AGENT': 'Mozilla/5.0', 
                 'accept': 'application/json, text/plain, */*',
                 'accept-encoding': 'gzip, deflate, br', 
                 'accept-language': 'en-US,en;q=0.9',
                 'cookie':'_ga=GA1.1.2135650958.1699493067; _fbp=fb.1.1699493068807.546237007; OptanonAlertBoxClosed=2023-11-18T00:27:06.194Z; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Nov+27+2023+16%3A45%3A47+GMT-0800+(Pacific+Standard+Time)&version=6.23.0&isIABGlobal=false&hosts=&consentId=3f8042c6-62c9-459e-b451-8d2bb2d2bb0c&interactionCount=2&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&geolocation=US%3BCA&AwaitingReconsent=false; _ga_HKPPXV27L6=GS1.1.1701132344.7.1.1701132381.23.0.0; _ga_30LZ5B848R=GS1.1.1701132344.7.1.1701132381.23.0.0; incap_ses_2110_2829404=nmuEMn+X8GCYRr3tTzpIHdc5dWUAAAAAkCfehUkETn3bkUOXJJF9TQ==; AramarkContextInfo=32|{a906eb02-9a20-4c32-83ab-4c44aa7ecae2}|Education; visid_incap_2829404=m7L0fKSVQImqnJ+jFhGClyaxe2UAAAAAQUIPAAAAAAADAaxNzlBTEpAUu2jSBVX4; incap_ses_226_2829404=xksGaJqYfybZsHCSP+oiAyaxe2UAAAAA3Vaw3MCEMfaqz1xnNV5LOw==; __CLAnonymousUser=024VtvBU8JFjAEXI1VYrJfhiw==8E4JagTsXCI5TvhsckSrGtRhrtg8Ba2nvKbKi0oEEqer94E3xhYXibEhXRE+ld898AF9ph8JUW+dQDVwl/vOyVTizKg1NWUaH2cbV0iwhMfa35zlwhSQGRlniC+jmeXfmRIseGcC0/YDWXtDWGdeYBuDzZzLdLVEI+QiZupaYIh7WGLXyKcXB7N2n6NJ97cCMXdFegb240euayuoKELQ3dHATOy/IaiALslPWTiCEk7PEZe6efKRSkreG6QwUVw4TRsRxPbMJ+4hjSVbLq7psIo1+YIE/ZSilIrY/izKcsl2E4Gifa7DoejmUkoscdE39E1gsjdjhrmdBkhukGlMyk4FoRxGNmbnqrnejXlTbe5vLEGV6+Ux8IDe815T5qS/RwjoSJrle6gL2ixz/80RNLTx0WUNujf0DeOMV5/g8RS8eR8ePpGbOg5z1MuccNOQdaboGDa4FAkA9aR2LaIA1xgyhFPEMN2gTRwD7C5G1Vh16GMxgSyZF/aguI2FzcseaZr6FL90qvLeWY6yCg8m7VQQ0TxPSaqQufmYP8Zn53nBegruLSl6T9nXGYFxiaH14Dt2Uwzn5lC/yQAEeEzstHgS0h7+jLfP87RwaWIVjQzHdR4YryHYED++mWj7DlZ5F6lrl4dT/7SGOXfeJhXmb+NF9FAAj8pIHbo8u686DsNBGwXjJmxouuZ2dH5iwV8rAjn0cMayfkfFxRLqaqs6lG+s+MDIWX758R+2Xfjz7n0bBNhtSI1IFUU8DjxsqabUtBnXNerMq+NqYBZSTz1sdvCbBKZkFwZdlLdzvwEEt58=' }
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

    try:
        url = 'https://uci.campusdish.com/LocationsAndMenus/'
        if restaurant == 'Anteatery':
            url += 'TheAnteatery'
        else:
            url += restaurant
        schedule = {}
        soup = bs(requests.get(url).text, 'html.parser')
        meal_period = soup.select('.mealPeriod')

        location_times = soup.select('span[class=location__times]')
        times = []
        meals = []

        for time in location_times:
            times.append(time.getText().split(' - '))
        times.append([times[-2][0],times[-1][1]]) #extended dinner
        for meal in meal_period:
            meals.append(meal.getText().lower())
        # print(times)
        # Hard coded to match the UCI website schedule
        weekday = [(meals[0], times[0]), #Breakfast
                (meals[2], times[3]), #Lunch
                (meals[3], times[4]), #Dinner
               (meals[3], times[-1])] #Extended dinner time because of latenight
        weekend = [(meals[0], times[1]), #Breakfast
                (meals[1], times[2]), #Brunch
                (meals[3], times[4]) #Dinner
        ]
        # if today is in the range of 0-4, it is Weekday otherwise weekend
        today = datetime.now().weekday()
        if today>4:
           data=weekend
        else:
            data = weekday
            if today ==4:
                del data[-1]
            else:
                del data[-2]
        
        for (meal, time) in data:
            if re.match(r"^\d?\d:\d\d(AM|PM)$", time[0]) and re.match(r"^\d?\d:\d\d(AM|PM)$", time[1]):
                start = normalize_time_from_str(time[0])
                end = normalize_time_from_str(time[1])
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
    except:
        # return hardcoded schedule
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
        if day_of_week >= 4: # if friday or later, there's no latenight
            schedule["dinner"]["end"] = 2000
            if day_of_week >= 5: # if it's the weekend, lunch is brunch, and breakfast starts later
                schedule["brunch"] = schedule["lunch"]
                del schedule["lunch"]
                schedule["breakfast"]["start"] = 900
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
