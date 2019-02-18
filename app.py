from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from lib.models import db

app = Flask(__name__)

# app.config['SQLALCHEMY_ECHO'] = True
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite://'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dqcAuyHTS8nR@scrobblesdb.cbz9hqclu0ef.us-east-1.rds.amazonaws.com/scrobbles?charset=utf8'
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