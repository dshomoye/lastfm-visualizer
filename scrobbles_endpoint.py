from flask import Blueprint,request, jsonify, Response, make_response
from lib.data import Scrobbleswrangler
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
    except Exception:
        bad_date_request = {"errors": [
            "failed to get begin/end date from request"
        ]}
        return make_response(jsonify(bad_date_request),400)
    scobble_data = Scrobbleswrangler(lastfm_username=lf_username)
    track_scrobbles = scobble_data.get_scrobbles_in_period(start_period=start,end_period=end)
    track_scrobbles = {
        "date": f'{start} {end}',
        "scrobbles": track_scrobbles
        }
    return jsonify(track_scrobbles)

@scrobbles_api.route('/')
def scrobbles_index():
    return "scrobbles index"