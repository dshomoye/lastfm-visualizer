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
    print(type(app))
    app.config['TESTING'] = True
    os.environ['TESTING'] = "True"
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
        "end": "2019-01-28",
        "scale":"days"
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/frequency',data=json.dumps(data),content_type='application/json')
    expected_result = {
        'end': '2019-01-28 00:00:00', 
        'frequency': {
            '2019-01-23': 57, 
            '2019-01-24': 25, 
            '2019-01-25': 3, 
            '2019-01-26': 34, 
            '2019-01-27': 40
        }, 
        'start': '2019-01-23 00:00:00'
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
	"end": "2019-01-28",
	"limit":3
    }
    r = client.get(f'/scrobbles/{LF_TEST_USERNAME}/top-tracks',data=json.dumps(data),content_type='application/json')
    print(r.json)
    assert r.status_code == 200
    expected_result = {
        'date': '2019-01-23 00:00:00 2019-01-28 00:00:00', 
        'top tracks': [
        {
            'played': 7, 'track': {
                'album': 'No Budget (feat. Rich The Kid)', 'artist': 'Kid Ink', 'title': 'No Budget (feat. Rich The Kid)'
            }
        },
        {'played': 7, 'track': {
            'album': 'Rumors (With Sofia Carson)', 'artist': 'R3hab', 'title': 'Rumors (With Sofia Carson)'
            }
        },
        {
            'played': 3, 'track': {
                'album': 'Meant To Love You', 'artist': 'Jauz', 'title': 'Meant To Love You'
            }
        }
        ]
    }
    assert r.json == expected_result



