import os
import pytest
import json
import responses

from lastfm_visualizer.app import app

LF_TEST_USERNAME="testuser"
LF_API = "http://ws.audioscrobbler.com/2.0"
DUMMY_LF_DATA_PATH = 'tests/data.json'



@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client
    if os.path.exists(f'{LF_TEST_USERNAME}.scrobbles'):
        os.remove(f'{LF_TEST_USERNAME}.scrobbles')


def standard_data_request_callback(request):
    with open(DUMMY_LF_DATA_PATH) as f:
        resp_body = json.load(f)
    headers = {'content-type': 'application/json'}
    return (200, headers, json.dumps(resp_body))


def test_ping_endpoint(client):
    r = client.get('/ping')
    assert b'Hello World!' in r.data


@responses.activate
def test_frequency_endpoint_returns_right_frequency(client):
    lf_endpoint = f'{LF_API}/?method=user.getRecentTracks&user={LF_TEST_USERNAME}'
    responses.add_callback(
        responses.GET, lf_endpoint,
        callback=standard_data_request_callback,
        content_type='application/json',
    )
    data = {
        "start":"2019-01-23",
        "end": "2019-01-25",
        "scale":"days"
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/frequency',data=json.dumps(data),content_type='application/json')
    expected_result = {
        "end": "2019-01-25 00:00:00+00:00",
        "frequency": {
            "2019-01-23": 151,
            "2019-01-24": 30
        },
        "start": "2019-01-23 00:00:00+00:00"
    }
    assert r.status_code == 200
    assert r.json == expected_result


@responses.activate
def test_top_tracks_endpoint_returns_right_result(client):
    lf_endpoint = f'{LF_API}/?method=user.getRecentTracks&user={LF_TEST_USERNAME}'
    responses.add_callback(
        responses.GET, lf_endpoint,
        callback=standard_data_request_callback,
        content_type='application/json',
    )
    data = {
	"start":"2019-01-23",
	"end": "2019-01-25",
	"limit":3
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/top-tracks',data=json.dumps(data),content_type='application/json')
    assert r.status_code == 200
    expected_result = {
        "date": "2019-01-23 00:00:00+00:00 2019-01-25 00:00:00+00:00",
        "top tracks": [
            {
                "played": 68,
                "track": {
                    "album": "The Wave",
                    "artist": "R3hab",
                    "title": "Rumors (With Sofia Carson)"
                }
            },
            {
                "played": 9,
                "track": {
                    "album": "Rumors (With Sofia Carson)",
                    "artist": "R3hab",
                    "title": "Rumors (With Sofia Carson)"
                }
            },
            {
                "played": 6,
                "track": {
                    "album": "No Budget (feat. Rich The Kid)",
                    "artist": "Kid Ink",
                    "title": "No Budget (feat. Rich The Kid)"
                }
            }
        ]
    }
    assert r.json == expected_result


@responses.activate
def test_top_albums_endpoint_returns_right_result(client):
    lf_endpoint = f'{LF_API}/?method=user.getRecentTracks&user={LF_TEST_USERNAME}'
    responses.add_callback(
        responses.GET, lf_endpoint,
        callback=standard_data_request_callback,
        content_type='application/json',
    )
    data = {
	"start":"2019-01-23",
	"end": "2019-01-25",
	"limit":3
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/top-albums',data=json.dumps(data),content_type='application/json')
    assert r.status_code == 200
    expected_result = {
        "date": "2019-01-23 00:00:00+00:00 2019-01-25 00:00:00+00:00",
        "top albums": [
            {
                "album": "The Wave",
                "album artist": "R3hab",
                "played": 68
            },
            {
                "album": "Rumors (With Sofia Carson)",
                "album artist": "R3hab",
                "played": 9
            },
            {
                "album": "No Budget (feat. Rich The Kid)",
                "album artist": "Kid Ink",
                "played": 6
            }
        ]
    }
    assert r.json == expected_result

@responses.activate
def test_top_artists_endpoint_returns_right_result(client):
    lf_endpoint = f'{LF_API}/?method=user.getRecentTracks&user={LF_TEST_USERNAME}'
    responses.add_callback(
        responses.GET, lf_endpoint,
        callback=standard_data_request_callback,
        content_type='application/json',
    )
    data = {
	"start":"2019-01-23",
	"end": "2019-01-25",
	"limit":3
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/top-artists',data=json.dumps(data),content_type='application/json')
    assert r.status_code == 200
    expected_result = {
        "date": "2019-01-23 00:00:00+00:00 2019-01-25 00:00:00+00:00",
        "top artists": [
            {
                "artist": "R3hab",
                "played": 77
            },
            {
                "artist": "Kid Ink",
                "played": 6
            }
        ]
    }
    assert r.json == expected_result

@responses.activate
def test_scrobbles_endpoint_returns_scrobbles(client):
    lf_endpoint = f'{LF_API}/?method=user.getRecentTracks&user={LF_TEST_USERNAME}'
    responses.add_callback(
        responses.GET, lf_endpoint,
        callback=standard_data_request_callback,
        content_type='application/json',
    )
    data = {
        "start":"2019-01-23 00-00-00",
        "end": "2019-01-23 12-00-00"
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}',data=json.dumps(data),content_type='application/json')
    assert r.status_code == 200
    expected_result = {
        "date": "2019-01-23 00:00:00+00:00 2019-01-23 12:00:00+00:00",
        "scrobbles": [
            {
                "date": "Wed, 23 Jan 2019 11:57:47 GMT",
                "track": {
                    "album": "The Last Rocket",
                    "artist": "Takeoff",
                    "title": "She Gon Wink"
                }
            },
            {
                "date": "Wed, 23 Jan 2019 11:54:49 GMT",
                "track": {
                    "album": "Splashin",
                    "artist": "Rich the Kid",
                    "title": "Splashin"
                }
            },
            {
                "date": "Wed, 23 Jan 2019 11:51:22 GMT",
                "track": {
                    "album": "Feelin Like",
                    "artist": "Flipp Dinero",
                    "title": "Feelin Like"
                }
            },
            {
                "date": "Wed, 23 Jan 2019 11:48:50 GMT",
                "track": {
                    "album": "The Wave",
                    "artist": "R3hab",
                    "title": "Rumors (With Sofia Carson)"
                }
            }
        ]
    }
    assert r.json == expected_result