from flask import Blueprint,request, jsonify, Response, make_response, current_app
from lib.errors import LastFMUserNotFound, ScrobbleFetchFailed, InValidParameter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.tz import UTC # type: ignore
import typing
from lib.database import DbHelper
from lib.lastfm import LastFMHelper

scrobbles_api = Blueprint('scrobbles',__name__)


@scrobbles_api.route('/<username>/update', methods=['POST','GET'])
def update_user_scrobbles(username):
    current_app.logger.info(f"Updating scrobbles for user {username}")
    try:
        lf = LastFMHelper(username=username)
        r = lf.get_or_update_user_scrobbles()
        if r: return "updated", 200
    except Exception as e:
        return __return_response_for_exception(e)
    

@scrobbles_api.route('/<lf_username>', methods=['GET'])
def get_scrobbles(lf_username):
    current_app.logger.info(f"Getting scrobbles for user {lf_username}")
    try:
        try:
            start = parse(_get_required_param(_get_request_param(request),'start')).replace(tzinfo=UTC)
            end = parse(_get_required_param(_get_request_param(request),'end')).replace(tzinfo=UTC)
        except ValueError as e:
            raise InValidParameter("Error processing request at start/end parameter")
        db = DbHelper(lf_username)
        track_scrobbles = {
            "start" : f'{start}',
            "end" : f'{end}',
            "scrobbles": db.get_scrobbles_in_period(
                start_period=start,end_period=end)
        }
        return jsonify(track_scrobbles)
    except Exception as e:
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-tracks', methods=['GET'])
def get_top_tracks(lf_username):
    current_app.logger.info(f"Getting top tracks for user {lf_username}")
    try:
        try:
            start = parse(_get_required_param(_get_request_param(request),'start')).replace(tzinfo=UTC)
            end = parse(_get_required_param(_get_request_param(request),'end')).replace(tzinfo=UTC)
        except ValueError as e:
            raise InValidParameter("Error processing request at start/end parameter")
        limit = _get_optional_or_default_param(_get_request_param(request),'limit')
        if not limit: limit = 5
        db = DbHelper(lf_username)
        top_tracks = {
            "start" : f'{start}',
            "end" : f'{end}',
            "top tracks": db.get_top_tracks_for_period(start,end,int(limit))
        }
        return jsonify(top_tracks)
    except Exception as e:
        return __return_response_for_exception(e)

@scrobbles_api.route('/<lf_username>/top-albums', methods=['GET'])
def get_top_albums(lf_username):
    current_app.logger.info(f"Getting top albums for user {lf_username}")
    try:
        try:
            start = parse(_get_required_param(_get_request_param(request),'start')).replace(tzinfo=UTC)
            end = parse(_get_required_param(_get_request_param(request),'end')).replace(tzinfo=UTC)
        except ValueError as e:
            raise InValidParameter("Error processing request at start/end parameter")
        limit = _get_optional_or_default_param(_get_request_param(request),'limit')
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
    current_app.logger.info(f"Getting top artist for user {lf_username}")
    try:
        try:
            start = parse(_get_required_param(_get_request_param(request),'start')).replace(tzinfo=UTC)
            end = parse(_get_required_param(_get_request_param(request),'end')).replace(tzinfo=UTC)
        except ValueError as e:
            raise InValidParameter("Error processing request at start/end parameter")
        limit = _get_optional_or_default_param(_get_request_param(request),'limit')
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
    current_app.logger.info(f"Getting listening frequency for user {lf_username}")
    try:
        try:
            start = parse(_get_required_param(_get_request_param(request),'start')).replace(tzinfo=UTC)
            end = parse(_get_required_param(_get_request_param(request),'end')).replace(tzinfo=UTC)
            scale = _get_required_param(_get_request_param(request),'scale')
        except ValueError as e:
            raise InValidParameter("Error processing request at start/end parameter")
        db = DbHelper(lf_username)
        frequency = {
            "start": str(start),
            "end": str(end),
            "frequency": db.get_track_count_in_period(start_period=start,end_period=end,unit=scale)
        }
        return jsonify(frequency)
    except Exception as e:
        return __return_response_for_exception(e)
            

def __return_response_for_exception(error: Exception) -> Response:
    r = [{"error": str(error)},500]
    if isinstance(error,LastFMUserNotFound):
        r[1] = 404
    elif isinstance(error,ScrobbleFetchFailed):
        r[0] = {"error":f"unable to get scrobbles from lastFM {error}"}
    elif isinstance(error, InValidParameter):
        r = [{"error": str(error)},400]

    return make_response(jsonify(r[0]), r[1])

def _get_optional_or_default_param(params,param):
    if param in params:
        return params[param]
    else:
        current_app.logger.info(f"No limit specified, defaulting to 5")
        defaults = {
            'limit': 5
        }
        return defaults[param]

def _get_required_param(params,param):
    if param in params:
        return params[param]
    else:
        current_app.logger.info(f"missing required argument {param}")
        raise InValidParameter(f"Error with request argument at {param}")

def _get_request_param(r):
    if r.args:
        return r.args
    elif r.json:
        return r.json
    else:
        current_app.logger.warning(f"No arguments/parameters in request!")
        return None


