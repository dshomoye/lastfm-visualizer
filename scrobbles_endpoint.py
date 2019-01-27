from flask import Blueprint,request, jsonify, Response, make_response
from lib.data import Scrobbleswrangler
from errors import LastFMUserNotFound
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

scrobbles_api = Blueprint('scrobbles',__name__)

@scrobbles_api.route('/<lf_username>',methods=['GET'])
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

@scrobbles_api.route('/<lf_username>/top-tracks',methods=['GET'])
def get_top_tracks(lf_username):
    try:
        req = request.json
        start = datetime.now()
        end = start - relativedelta(days=1)
        limit=5
        if 'start' in req:
            start = parse(req['start'])
            end = parse(req['end'])
        if 'limit' in req:
            limit = req['limit']
        scobble_data = Scrobbleswrangler(lastfm_username=lf_username)
        top_tracks = {
            "date": f'{start} {end}',
            "top tracks": scobble_data.get_top_tracks_for_period(start,end,limit)
        }
        return jsonify(top_tracks)
    except Exception as e:
        return __return_response_for_exception(e)

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

