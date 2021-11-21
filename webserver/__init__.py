"""
The flask application package.
"""
from os import environ
from webserver.server import app

HOST = environ.get('SERVER_HOST', 'localhost')
try:
    PORT = int(environ.get('SERVER_PORT', '5555'))
except ValueError:
    PORT = 5555


def run_server(callback):
    app.callback = callback
    app.run(HOST, PORT)
