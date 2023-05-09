# run this file with `pytest cache_test.py` from the project root directory, with the .env file on the same level.
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
from http.server import HTTPServer
import requests
from threading import Thread
import json
import pytest






def test_with_cache(monkeypatch: pytest.MonkeyPatch):
    """
    This is a near-copy of the test in test_server, except it turns on caching.
    It isn't in the pytest folder because I don't want to expose the firebase credentials
    in the github workflow. If you know a way to get the env vars to the github workflow
    auto tests without putting them in source, go ahead and implement it.
    """

    monkeypatch.setenv("USE_CACHE","TRUE")

    from api.index import handler
    from api.util import APIResponse
    def start_server(port: int=3003):
        HTTPServer(("",port),handler).handle_request()

    p = Thread(target=start_server)
    p.start()
    res = requests.get("http://localhost:3003/api?location=brandywine")

    assert res.status_code == 200
    print(res.content.decode('utf-8'))
    body = json.loads(res.content)

    parsed_body = APIResponse(**body)

    print(parsed_body)

    p.join()
