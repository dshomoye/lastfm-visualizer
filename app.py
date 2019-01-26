from flask import Flask
from scrobbles_endpoint import scrobbles_api

app = Flask(__name__)

app.debug = True
app.register_blueprint(scrobbles_api, url_prefix='/scrobbles')


@app.route('/')
def home():
    return 'App home'


if __name__ == '__main__':
    app.run()