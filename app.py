from flask import Flask


app = Flask(__name__)

app.debug = True


@app.route('/')
def home():
    return 'App home'


if __name__ == '__main__':
    app.run()