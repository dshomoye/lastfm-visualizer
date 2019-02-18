import os
import pytest
import json
import responses

from lastfm_visualizer.app import app
from lib.database import DbHelper

LF_TEST_USERNAME="testuser"
LF_API = "http://ws.audioscrobbler.com/2.0"
DUMMY_LF_DATA_PATH = 'tests/data.json'
TEST_DB = 'tests/testdb.db'



@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI']=f'sqlite:///{TEST_DB}'
    client = app.test_client()

    yield client
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


def standard_data_request_callback(request):
    with open(DUMMY_LF_DATA_PATH) as f:
        resp_body = json.load(f)
    headers = {'content-type': 'application/json'}
    return (200, headers, json.dumps(resp_body))


def test_ping_endpoint(client):
    r = client.get('/ping')
    assert b'Hello World!' in r.data


@responses.activate
def test_an_update_of_scrobbles(client):
    lf_endpoint = f'{LF_API}/?method=user.getRecentTracks&user={LF_TEST_USERNAME}'
    responses.add_callback(
        responses.GET, lf_endpoint,
        callback=standard_data_request_callback,
        content_type='application/json',
    )
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/update')
    assert r.status_code == 200
    print(r.data)


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
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/update')
    print(r.data)
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/frequency',data=json.dumps(data),content_type='application/json')
    expected_result = {
        "end": "2019-01-25 00:00:00+00:00",
        "frequency": {
            "2019-01-23": 154,
            "2019-01-24": 25
        },
        "start": "2019-01-23 00:00:00+00:00"
    }
    print(r.data)
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
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/update')

    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/top-tracks',data=json.dumps(data),content_type='application/json')
    expected_result = {
        "end": "2019-01-25 00:00:00+00:00",
        "start": "2019-01-23 00:00:00+00:00",
        "top tracks": [
            {
                "album": "Rumors (With Sofia Carson)",
                "artist": "R3hab",
                "played": 77,
                "track": "Rumors (With Sofia Carson)"
            },
            {
                "album": "No Budget (feat. Rich The Kid)",
                "artist": "Kid Ink",
                "played": 7,
                "track": "No Budget (feat. Rich The Kid)"
            },
            {
                "album": "Long Live the Champion",
                "artist": "KB",
                "played": 3,
                "track": "Long Live the Champion"
            }
        ]
    }
    print(r.json)
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
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/update')

    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/top-albums',data=json.dumps(data),content_type='application/json')
    assert r.status_code == 200
    expected_result = {
        "end": "2019-01-25 00:00:00+00:00",
        "start": "2019-01-23 00:00:00+00:00",
        "top albums": [
            {
                "album": "The Wave",
                "artist": "R3hab",
                "played": 68
            },
            {
                "album": "Rumors (With Sofia Carson)",
                "artist": "R3hab",
                "played": 9
            },
            {
                "album": "No Budget (feat. Rich The Kid)",
                "artist": "Kid Ink",
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
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/update')

    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/top-artists',data=json.dumps(data),content_type='application/json')
    assert r.status_code == 200
    expected_result = {
        "end": "2019-01-25 00:00:00+00:00",
        "start": "2019-01-23 00:00:00+00:00",
        "top artists": [
            {
                "artist": "R3hab",
                "played": 77
            },
            {
                "artist": "Kid Ink",
                "played": 7
            },
            {
                "artist": "KB",
                "played": 3
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
        "start":"2019-01-24 12:00:00",
        "end": "2019-01-24 12:30:00"
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/update')

    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}',data=json.dumps(data),content_type='application/json')
    assert r.status_code == 200
    expected_result = {
        "end": "2019-01-24 12:30:00+00:00",
        "scrobbles": [
            {
                "date": "Thu, 24 Jan 2019 12:28:48 GMT",
                "track": {
                    "album": "Scorpion",
                    "artist": "Drake",
                    "title": "In My Feelings"
                }
            },
            {
                "date": "Thu, 24 Jan 2019 12:25:30 GMT",
                "track": {
                    "album": "Championships",
                    "artist": "Meek Mill",
                    "title": "Going Bad (feat. Drake)"
                }
            },
            {
                "date": "Thu, 24 Jan 2019 12:21:39 GMT",
                "track": {
                    "album": "Nervous (feat. Lil Baby, Jay Critch & Rich the Kid)",
                    "artist": "Famous Dex",
                    "title": "Nervous (feat. Lil Baby, Jay Critch & Rich the Kid)"
                }
            },
            {
                "date": "Thu, 24 Jan 2019 12:17:41 GMT",
                "track": {
                    "album": "Queen (Deluxe)",
                    "artist": "Nicki Minaj",
                    "title": "gOOd fOrM (feaT. liL WaynE)"
                }
            },
            {
                "date": "Thu, 24 Jan 2019 12:12:14 GMT",
                "track": {
                    "album": "MoshPit (feat. Juice WRLD)",
                    "artist": "Kodak Black",
                    "title": "MoshPit (feat. Juice WRLD)"
                }
            },
            {
                "date": "Thu, 24 Jan 2019 12:09:30 GMT",
                "track": {
                    "album": "No Budget (feat. Rich The Kid)",
                    "artist": "Kid Ink",
                    "title": "No Budget (feat. Rich The Kid)"
                }
            },
            {
                "date": "Thu, 24 Jan 2019 12:06:12 GMT",
                "track": {
                    "album": "No Budget (feat. Rich The Kid)",
                    "artist": "Kid Ink",
                    "title": "No Budget (feat. Rich The Kid)"
                }
            },
            {
                "date": "Thu, 24 Jan 2019 12:02:02 GMT",
                "track": {
                    "album": "No Budget (feat. Rich The Kid)",
                    "artist": "Kid Ink",
                    "title": "No Budget (feat. Rich The Kid)"
                }
            }
        ],
        "start": "2019-01-24 12:00:00+00:00"
    }
    assert r.json == expected_result