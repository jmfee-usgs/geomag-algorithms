from __future__ import absolute_import, unicode_literals

import os
import flask

from . import database, login, session


def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    # configure using environment variables
    app.config.update(os.environ)

    # connect modules
    database.init_app(app)
    login.init_app(app)
    session.init_app(app)

    # add default route
    @app.route("/")
    def index():
        return "<h1>Restricted Page</h1>"

    return app
