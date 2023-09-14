import json
import os

import pytest
from requests_mock import ANY as REQUESTS_MOCK_ANY

from antares_client.config import config

API_RESPONSE_DIRECTORY = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "data", "api_responses"
)


@pytest.fixture()
def mock_api(requests_mock):
    files = [f for f in os.listdir(API_RESPONSE_DIRECTORY) if f.endswith(".json")]
    for file in files:
        with open(os.path.join(API_RESPONSE_DIRECTORY, file)) as f:
            response = json.load(f)
            path = file.replace(".json", "").replace("-", "/")
            requests_mock.get(config["ANTARES_API_BASE_URL"] + path, json=response)


@pytest.fixture()
def mock_api_404(requests_mock):
    requests_mock.register_uri(
        REQUESTS_MOCK_ANY,
        REQUESTS_MOCK_ANY,
        status_code=404,
        json={
            "errors": [
                {
                    "detail": "The requested URL was not found.",
                    "status": 404,
                    "title": "404 NOT FOUND",
                }
            ]
        },
    )


@pytest.fixture()
def mock_api_500(requests_mock):
    requests_mock.register_uri(
        REQUESTS_MOCK_ANY,
        REQUESTS_MOCK_ANY,
        status_code=500,
        json={
            "errors": [
                {
                    "detail": "The server encountered a problem.",
                    "status": 500,
                    "title": "500 Internal Server Error",
                }
            ]
        },
    )
