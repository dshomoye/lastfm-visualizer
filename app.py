from flask import Flask
import os
# from flask_sqlalchemy import SQLAlchemy
from lib.models import db

app = Flask(__name__)

rds_user = os.getenv('RDS_USER',"")
rds_p = os.getenv("RDS_SEC","")
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{rds_user}:{rds_p}@scrobblesdb.cbz9hqclu0ef.us-east-1.rds.amazonaws.com/scrobbles?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)

app.debug = True
from blueprints.scrobbles import scrobbles_api
app.register_blueprint(scrobbles_api, url_prefix='/scrobbles')


@app.route('/')
@app.route('/ping')
def home():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()