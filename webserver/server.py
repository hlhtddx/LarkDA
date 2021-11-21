"""
Routes and views for the flask application.
"""
from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def home():
    """Renders the home page."""
    return "Home page should not to accessed"


@app.route('/login_success')
def login_success():
    """process login success callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    app.callback.on_login_success(code)
    shutdown_server()
    return 'Login successfully. You can close this page now.'


@app.route('/shutdown')
def shutdown():
    """process shutdown callback"""
    shutdown_server()
    return "Shutting down..."


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
