from flask import Blueprint,request, jsonify, Response, make_response
from lib.data import Scrobbleswrangler
from lib.errors import LastFMUserNotFound
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

scrobbles_api = Blueprint('scrobbles',__name__)

@scrobbles_api.route('/<lf_username>', methods=['GET'])
def get_scrobbles(lf_username):
    req = request.json
    try:
        start = parse(req['start'])
        end = parse(req['end'])
        scobble_data = Scrobbleswrangler(lastfm_username=lf_username)
        track_scrobbles = {
            "date": f'{start} {end}',
            "scrobbles": scobble_data.get_scrobbles_in_period(
                start_period=start,end_period=end)
        }
        return jsonify(track_scrobbles)
    except Exception as e:
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-tracks', methods=['GET'])
def get_top_tracks(lf_username):
    try:
        req = request.json
        start = parse(req['start'])
        end = parse(req['end'])
        limit = req['limit']
        scobble_data = Scrobbleswrangler(lastfm_username=lf_username)
        top_tracks = {
            "date": f'{start} {end}',
            "top tracks": scobble_data.get_top_tracks_for_period(start,end,limit)
        }
        return jsonify(top_tracks)
    except Exception as e:
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-albums', methods=['GET'])
def get_top_albums(lf_username):
    try:
        req = request.json
        start = parse(req['start'])
        end = parse(req['end'])
        limit = req['limit']
        scobble_data = Scrobbleswrangler(lastfm_username=lf_username)
        top_tracks = {
            "date": f'{start} {end}',
            "top albums": scobble_data.get_top_albums_for_period(start,end,limit)
        }
        return jsonify(top_tracks)
    except Exception as e:
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-artists', methods=['GET'])
def get_top_artist(lf_username):
    try:
        req = request.json
        start = parse(req['start'])
        end = parse(req['end'])
        limit = req['limit']
        scobble_data = Scrobbleswrangler(lastfm_username=lf_username)
        top_tracks = {
            "date": f'{start} {end}',
            "top albums": scobble_data.get_top_artists_for_period(start,end,limit)
        }
        return jsonify(top_tracks)
    except Exception as e:
        return __return_response_for_exception(e)
    
@scrobbles_api.route('/<lf_username>/frequency', methods=['GET'])
def get_listening_frequency(lf_username):
    try:
        req = request.json
        start = parse(req['start'])
        end = parse(req['end'])
        scale = req['scale']
        scobble_data = Scrobbleswrangler(lastfm_username=lf_username)
        frequency = {
            "start": str(start),
            "end": str(end),
            "frequency": scobble_data.get_track_count_in_period(start_period=start,end_period=end,unit=scale)
        }
        return jsonify(frequency)
    except Exception as e:
        raise e
            

def __return_response_for_exception(error: Exception) -> Response:
    if isinstance(error,LastFMUserNotFound):
        user_not_found = {"errors": [str(error)]}
        return make_response(jsonify(user_not_found),404)
    if isinstance(error,ValueError) or isinstance(error,KeyError):
        bad_date_request = {"errors": ["missing attribute or bad date format" ]}
        return make_response(jsonify(bad_date_request),422)
    else:
        fetch_failed = {"errors": [str(error)]}
        return make_response(jsonify(fetch_failed), 400) 

