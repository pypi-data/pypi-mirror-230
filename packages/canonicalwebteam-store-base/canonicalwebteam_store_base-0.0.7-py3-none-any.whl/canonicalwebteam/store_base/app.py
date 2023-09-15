"""
Extensible flask application base for all stores.

It gets response from the store_api and it extends

each store blueprint to make a complete application
"""
from flask import session, make_response
from canonicalwebteam.flask_base.app import FlaskBase
import canonicalwebteam.store_base.utils.config as config
from canonicalwebteam.store_base.auth.views import auth
from canonicalwebteam.store_base.packages.views import store_packages
from canonicalwebteam.store_base.utils.extensions import csrf
from canonicalwebteam.store_base.handlers import set_handlers
from canonicalwebteam.store_base.sample_blueprint.views import sample_bp


def create_app(
    app_name, store_bp=sample_bp, utility_processor=None, testing=False
):
    app = FlaskBase(__name__, app_name)

    app.register_blueprint(store_bp)
    app.register_blueprint(store_packages)
    app.register_blueprint(auth)

    app.config.from_object(config)
    app.testing = testing

    csrf.init_app(app)
    set_handlers(app, utility_processor)

    @app.route("/account.json")
    def get_account_json():
        """
        A JSON endpoint to request login status
        """
        account = None

        if "account" in session:
            account = session["account"]

        response = {"account": account}
        response = make_response(response)
        response.headers["Cache-Control"] = "no-store"

        return response

    return app
