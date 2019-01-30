from flask import Flask
from blueprints.scrobbles import scrobbles_api

app = Flask(__name__)

app.debug = True
app.register_blueprint(scrobbles_api, url_prefix='/scrobbles')


@app.route('/ping')
def home():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()