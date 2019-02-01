from flask import Blueprint,request, jsonify, Response, make_response
from lib.data import Scrobbleswrangler
from lib.errors import LastFMUserNotFound, ScrobbleFetchFailed
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.tz import UTC
import typing

scrobbles_api = Blueprint('scrobbles',__name__)

__scrobblewranglers: typing.Dict[str,Scrobbleswrangler] = {}

@scrobbles_api.route('/<lf_username>', methods=['GET'])
def get_scrobbles(lf_username):
    req = request.json
    try:
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        #end = end.replace(tzinfo=UTC)
        #start = start.replace(tzinfo=UTC)
        scobble_data = __get_scrobble_data(lf_username)
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
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        limit = req['limit']
        scobble_data = __get_scrobble_data(lf_username)
        top_tracks = {
            "date": f'{start} {end}',
            "top tracks": scobble_data.get_top_tracks_for_period(start,end,int(limit))
        }
        return jsonify(top_tracks)
    except Exception as e:
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-albums', methods=['GET'])
def get_top_albums(lf_username):
    try:
        req = request.json
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        limit = req['limit']
        scobble_data = __get_scrobble_data(lf_username)
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
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        limit = req['limit']
        scobble_data = __get_scrobble_data(lf_username)
        top_tracks = {
            "date": f'{start} {end}',
            "top artists": scobble_data.get_top_artists_for_period(start,end,limit)
        }
        return jsonify(top_tracks)
    except Exception as e:
        return __return_response_for_exception(e)
    
@scrobbles_api.route('/<lf_username>/frequency', methods=['GET'])
def get_listening_frequency(lf_username):
    try:
        req = request.json
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        scale = req['scale']
        scobble_data = __get_scrobble_data(lf_username)
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
    elif isinstance(error,ValueError) or isinstance(error,KeyError):
        bad_date_request = {"errors": ["missing attribute or bad date format" ]}
        return make_response(jsonify(bad_date_request),422)
    elif isinstance(error,ScrobbleFetchFailed):
        e = {"errors":["unable to get scrobbles from lastFM",f"{error}"]}
        return make_response(jsonify(e),500)
    else:
        fetch_failed = {"errors": [str(error)]}
        return make_response(jsonify(fetch_failed), 400) 

def __get_scrobble_data(lf_username: str) -> Scrobbleswrangler:
    if lf_username not in __scrobblewranglers:
        __scrobblewranglers[lf_username] = Scrobbleswrangler(lastfm_username=lf_username)
    return __scrobblewranglers[lf_username]
    


