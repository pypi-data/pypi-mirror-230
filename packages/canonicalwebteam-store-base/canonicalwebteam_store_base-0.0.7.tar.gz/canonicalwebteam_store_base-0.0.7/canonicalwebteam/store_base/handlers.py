import flask
from flask import render_template

from canonicalwebteam.store_api.exceptions import (
    StoreApiError,
    StoreApiConnectionError,
    StoreApiResourceNotFound,
    StoreApiResponseDecodeError,
    StoreApiResponseErrorList,
    StoreApiResponseError,
    StoreApiTimeoutError,
)


def set_handlers(app, store_utility_processor):
    @app.context_processor
    def utility_processor():
        return store_utility_processor()

    @app.errorhandler(500)
    @app.errorhandler(501)
    @app.errorhandler(502)
    @app.errorhandler(504)
    @app.errorhandler(505)
    def internal_error(error):
        error_name = getattr(error, "name", type(error).__name__)
        return_code = getattr(error, "code", 500)

        supress_sentry = False
        if type(error).__name__ == "BadGateway":
            supress_sentry = True

        if not app.testing and not supress_sentry:
            app.extensions["sentry"].captureException()

        return (
            flask.render_template("50X.html", error_name=error_name),
            return_code,
        )

    @app.errorhandler(503)
    def service_unavailable(error):
        return render_template("503.html"), 503

    @app.errorhandler(404)
    @app.errorhandler(StoreApiResourceNotFound)
    def handle_resource_not_found(error):
        return render_template("404.html", message=str(error)), 404

    # @app.errorhandler(ApiTimeoutError)
    @app.errorhandler(StoreApiTimeoutError)
    def handle_connection_timeout(error):
        status_code = 504
        return (
            render_template(
                "50X.html", error_message=str(error), status_code=status_code
            ),
            status_code,
        )

    @app.errorhandler(StoreApiResponseDecodeError)
    @app.errorhandler(StoreApiResponseError)
    @app.errorhandler(StoreApiConnectionError)
    @app.errorhandler(StoreApiError)
    def store_api_error(error):
        status_code = 502
        return (
            render_template(
                "50X.html", error_message=str(error), status_code=status_code
            ),
            status_code,
        )

    @app.errorhandler(StoreApiResponseErrorList)
    def handle_store_api_error_list(e):
        if e.status_code == 404:
            return render_template("404.html", message="Entity not found"), 404

        status_code = 502
        if e.errors:
            errors = ", ".join([e.get("message") for e in e.errors])
            return (
                render_template(
                    "500.html", error_message=errors, status_code=status_code
                ),
                status_code,
            )

        return (
            render_template("500.html", status_code=status_code),
            status_code,
        )
