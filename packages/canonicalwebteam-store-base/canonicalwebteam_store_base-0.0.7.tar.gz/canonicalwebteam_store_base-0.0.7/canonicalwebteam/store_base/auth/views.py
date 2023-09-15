import talisker
from canonicalwebteam.candid import CandidClient
from canonicalwebteam.store_base.utils.config import PACKAGE_PARAMS
from flask import (
    Blueprint,
    session,
    redirect,
    request,
    make_response,
    abort,
    current_app as app,
)
from flask_wtf.csrf import generate_csrf, validate_csrf

from canonicalwebteam.store_base.auth.authentication import (
    empty_session,
    is_authenticated,
)
from canonicalwebteam.store_base.auth.logic import get_macaroon_response
from canonicalwebteam.store_base.utils.helpers import is_safe_url

# Login blueprint should be passed in at store level for now
auth = Blueprint("auth", __name__)

request_session = talisker.requests.get_session()
candid = CandidClient(request_session)


@auth.route("/logout")
def logout():
    empty_session(session)
    # should redirect to store landing page
    return "user successfully logged out"


@auth.route("/login")
def login():
    """
    Handles the login process for the user.

    Checks if the user is already authenticated
    Redirects authenticated user to the landing page.

    Sets the account macaroon if not authenticated
    Generates a callback URL and redirects unauthenticated
    users to the callback url


    Returns:
        flask.Response: Redirects the user to the login URL.
    """
    app_name = app.name
    store_publisher = PACKAGE_PARAMS[app_name]["publisher"]
    publisher_api = store_publisher(request_session)
    resp = get_macaroon_response(app_name, publisher_api)

    macaroon_response = resp["macaroon_response"]
    if is_authenticated(session):
        response = make_response({"token": session["account-auth"]})
        response.status_code = 200
        return response

    session["account-macaroon"] = macaroon_response

    login_url = candid.get_login_url(
        macaroon=session["account-macaroon"],
        # callback_url = url_for("auth.login_callback", _external=True),
        # hardcoded temporarily
        callback_url="http://localhost:8045/login/callback",
        state=generate_csrf(),
    )

    # Next URL to redirect the user after the login
    next_url = request.args.get("next")

    if next_url:
        if not is_safe_url(next_url):
            return abort(400)
        session["next_url"] = next_url

    return redirect(login_url, 302)


@auth.route("/login/callback")
def login_callback():
    """
    Callback function that handles the login redirect.

    Retrieves necessary information from the login request,
    validates CSRF token, discharges tokens and macaroons,
    stores bakery authentication, and returns a response with
    the account authentication token.

    Returns:
        flask.Response: Response object containing the account
        authentication token.
    """

    app_name = app.name
    store_publisher = PACKAGE_PARAMS[app_name]["publisher"]
    publisher_api = store_publisher(request_session)
    resp = get_macaroon_response(app_name, publisher_api)
    exchange_macaroon = resp["exchange_macaroon_method"]
    code = request.args["code"]
    state = request.args["state"]

    # To avoid  csrf attack
    validate_csrf(state)

    discharged_token = candid.discharge_token(code)
    candid_macaroon = candid.discharge_macaroon(
        session["account-macaroon"], discharged_token
    )

    # store bakery authentication
    issued_macaroon = candid.get_serialized_bakery_macaroon(
        session["account-macaroon"], candid_macaroon
    )
    session["account-auth"] = exchange_macaroon(issued_macaroon)
    session.update(publisher_api.macaroon_info(session["account-auth"]))

    response = make_response({"token": session["account-auth"]})
    response.status_code = 200
    return response
