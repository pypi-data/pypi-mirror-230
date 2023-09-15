import functools
import flask

from canonicalwebteam.store_base.auth.authentication import is_authenticated


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated(flask.session):
            return flask.redirect(
                flask.url_for("auth.login", next=flask.request.path)
            )
        return f(*args, **kwargs)

    return decorated_function
