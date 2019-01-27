from flask import Blueprint,request, jsonify, Response, make_response
from lib.data import Scrobbleswrangler
from errors import LastFMUserNotFound
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse

scrobbles_api = Blueprint('scrobbles',__name__)

@scrobbles_api.route('/<lf_username>',methods=['GET'])
def scrobbles(lf_username):
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
    except LastFMUserNotFound as e:
        user_not_found = {"errors": str(e)}
        return make_response(jsonify(user_not_found),404)
    except ValueError:
        bad_date_request = {"errors": ["missing attribute or bad date format" ]}
        return make_response(jsonify(bad_date_request),422)
    except Exception as e:
        fetch_failed = {"errors": [str(e)]}
        return make_response(jsonify(fetch_failed), 400)


@scrobbles_api.route('/')
def scrobbles_index():
    return "scrobbles index"