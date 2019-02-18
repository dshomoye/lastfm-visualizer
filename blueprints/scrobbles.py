from flask import Blueprint,request, jsonify, Response, make_response
# from lib.data import Scrobbleswrangler
from lib.errors import LastFMUserNotFound, ScrobbleFetchFailed
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.tz import UTC # type: ignore
import typing
from lib.database import DbHelper
import lib.database as db
from lib.lastfm import LastFMHelper

scrobbles_api = Blueprint('scrobbles',__name__)


@scrobbles_api.route('/<username>/update', methods=['POST','GET'])
def update_user_scrobbles(username):
    try:
        lf = LastFMHelper(username=username)
        r = lf.get_or_update_user_scrobbles()
        if r: return "updated", 200
    except Exception as e:
        raise e
        return __return_response_for_exception(e)
    

@scrobbles_api.route('/<lf_username>', methods=['GET'])
def get_scrobbles(lf_username):
    req = request.json
    try:
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        #end = end.replace(tzinfo=UTC)
        #start = start.replace(tzinfo=UTC)
        db = DbHelper(lf_username)
        track_scrobbles = {
            "start" : f'{start}',
            "end" : f'{end}',
            "scrobbles": db.get_scrobbles_in_period(
                start_period=start,end_period=end)
        }
        return jsonify(track_scrobbles)
    except Exception as e:
        raise e
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-tracks', methods=['GET'])
def get_top_tracks(lf_username):
    try:
        req = request.json
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        limit = req['limit']
        db = DbHelper(lf_username)
        top_tracks = {
            "start" : f'{start}',
            "end" : f'{end}',
            "top tracks": db.get_top_tracks_for_period(start,end,int(limit))
        }
        return jsonify(top_tracks)
    except Exception as e:
        raise e
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-albums', methods=['GET'])
def get_top_albums(lf_username):
    try:
        req = request.json
        start = parse(req['start']).replace(tzinfo=UTC)
        end = parse(req['end']).replace(tzinfo=UTC)
        limit = req['limit']
        db = DbHelper(lf_username)
        top_tracks = {
            "start" : f'{start}',
            "end" : f'{end}',
            "top albums": db.get_top_albums_for_period(start,end,limit)
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
        db = DbHelper(lf_username)
        top_tracks = {
            "start" : f'{start}',
            "end" : f'{end}',
            "top artists": db.get_top_artists_for_period(start,end,limit)
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
        db = DbHelper(lf_username)
        frequency = {
            "start": str(start),
            "end": str(end),
            "frequency": db.get_track_count_in_period(start_period=start,end_period=end,unit=scale)
        }
        return jsonify(frequency)
    except Exception as e:
        raise e
        return __return_response_for_exception(e)
            

def __return_response_for_exception(error: Exception) -> Response:
    if isinstance(error,LastFMUserNotFound):
        user_not_found = {"errors": [str(error)]}
        return make_response(jsonify(user_not_found),404)
    elif isinstance(error,ScrobbleFetchFailed):
        e = {"errors":["unable to get scrobbles from lastFM",f"{error}"]}
        return make_response(jsonify(e),500)
    else:
        fetch_failed = {"errors": [str(error)]}
        return make_response(jsonify(fetch_failed), 400) 


