import api.parsing
from datetime import datetime, timedelta
import pytz


def is_weekend(date: datetime) -> bool:
    'Given a datetime object, returns true if date is a weekend'
    return (date.weekday() == 5) or (date.weekday() == 6)

# Can be used to return a List with all of the menu information in the future
def week_menu(today: datetime) -> None:
    'Given a datetime object of a starting date, prints the following weeks menu for Anteatery and Brandywine'
    # Can be changed to fetch different number of days into the future. Currently fetches 7 days into the future.
    for i in range(1, 8):
        next_date = today + timedelta(days=i)
        date_string = next_date.strftime('%m/%d/%Y')
        # 3 Meals
        for x in range(3):
            print()
            if is_weekend(next_date) and x == 1:
                x = 3
            if x == 0:
                print("\nBREAKFAST:\n")
            elif x == 1:
                print("\nLUNCH:\n")
            elif x == 2:
                print("\nDINNER:\n")
            elif x == 3:
                print("\nBRUNCH:\n")
            print("Anteatery Menu:\n")
            anteatery_response = api.parsing.make_response_body(
                'anteatery', x, date_string)
            print(anteatery_response)
            brandywine_response = api.parsing.make_response_body(
                'brandywine', x, date_string)
            print("\nBrandywine Menu:\n")
            print(brandywine_response)


if __name__ == "__main__":
    # Set the time zone to Pacific Standard Time
    irvine_tz = pytz.timezone("America/Los_Angeles")
    # Get the current date and time in Irvine, California
    now = datetime.now(irvine_tz)
    week_menu(now)