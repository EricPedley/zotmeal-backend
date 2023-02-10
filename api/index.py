from http.server import BaseHTTPRequestHandler  # imported to have an http endpoint
import json
from typing import Union  # imported to format dict as json string
import urllib.parse  # imported to help parsing url componenets
import traceback  # for error handling
import os  # imported to get environment variables
from .util import is_valid_location, LOCATION_INFO
from .parsing import make_response_body


USE_CACHE = bool(os.getenv("USE_CACHE"))

print("Using cache" if USE_CACHE else "Not using cache")

# TODO: need to clear Firebase cache of outdated JSONS, should probably implement timer
# e.g. force refresh of cache every hour

if USE_CACHE:
    from .firebase_utils import get_db_reference

class InvalidQueryException(Exception):
    pass


class NotFoundException(Exception):
    pass


# to implement redirects see this: https://stackoverflow.com/questions/22701544/redirect-function-with-basehttprequesthandler
# redirects could be useful to just send the request straight to firebase


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        """
        Receive HTTP request and send response
        """

        try:
            _protocol, _url, path, params, raw_query, _ = urllib.parse.urlparse(
                "//" + self.path # prepending the // tricks urlparse into parsing correctly since self.path isn't the whole URL
            )  

            query = urllib.parse.parse_qs(raw_query)
        
            if path not in ("/api", "/api/"):
                raise NotFoundException

            if "location" not in query:
                raise InvalidQueryException("No location query parameter specified")

            
            location = query["location"][0]

            if not is_valid_location(location):
                raise InvalidQueryException(
                    f"The location specified is not valid. Valid locations: {list(LOCATION_INFO.keys())}"
                )

            meal = int(query["meal"][0]) if "meal" in query else None

            date = query["date"][0] if "date" in query else None
             # note: data gets decoded by urllib, so it will contain slashes.
            do_refresh = dict.get(query, 'refresh', [False])[0]

            if meal is None and date is not None:
                raise InvalidQueryException(
                    "You can't provide the date without the meal."
                )

            if USE_CACHE:
                print(f"date from query params: {date}")
                db_ref = get_db_reference(location, meal, date)
                db_data = db_ref.get()

                if db_data is None or do_refresh=='True':
                    data = make_response_body(location, meal, date)
                    db_ref.set(data)

                else:
                    data = db_data 

                mock_schedule = {
                    "breakfast": {
                        "start": 1,
                        "end": 2
                    },
                    "lunch": {
                        "start":2,
                        "end":3
                    },
                    "dinner": {
                        "start": 3,
                        "end": 4
                    }
                }
                
                if "schedule" not in data:
                    data["schedule"] = mock_schedule
                
                if "themed" not in data:
                    data["themed"] = []
            else:
                data = make_response_body(location, meal, date)

            self.send_response_with_body(
                status_code=200,
                body=json.dumps(data, ensure_ascii=False, indent=4),
            )

        except NotFoundException:
            self.send_response_with_body(
                status_code=404,
                body="Invalid path. The only one available is /api",
            )

        except InvalidQueryException as e:
            self.send_response_with_body(
                status_code=400,
                body=f"Invalid query parameters. Details: {e}",
            )

        except Exception as e:
            traceback.print_exc()
            self.send_response_with_body(
                status_code=500,
                body=f"Internal Server Error. Raise an issue on the github repo: https://github.com/EricPedley/zotmeal-backend. Details: {e}",
            )

    def send_response_with_body(self, status_code: int, body: Union[str, dict]) -> None:
        """
        Send an HTTP response with the given status code and body. Supports plaintext string or dict to be serialized as json.
        """

        self.send_response(status_code)
        if type(body) == str:
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dump(body))