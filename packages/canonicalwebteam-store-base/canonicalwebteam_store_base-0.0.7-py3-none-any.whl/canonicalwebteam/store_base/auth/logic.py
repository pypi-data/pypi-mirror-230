from flask import request


def get_macaroon_response(app_name, publisher_api):
    """
    Retrieves the macaroon response based on the provided app name
    and publisher API.

    Args:
        app_name (str): The name of the application.
        publisher_api: The publisher API object used for macaroon operations.

    Returns:
        dict: A dictionary containing the macaroon response, user redirect URL,
        and the method for exchanging macaroons.

    Note:
        - For "charmhub" the macaroon response includes a list of
          required permissions and a description based on the user agent.
        - For "snapcraft", the macaroon response is a string.
        A means of uniformity should be considered.
    """

    if app_name.startswith("charmhub"):
        user_agent = request.headers.get("User-Agent")
        macaroon_response = publisher_api.issue_macaroon(
            [
                "account-register-package",
                "account-view-packages",
                "package-manage",
                "package-view",
            ],
            description=f"charmhub.io - {user_agent}",
        )
        authenticated_user_redirect = "store.store_packages"
        exchange_macaroon_method = publisher_api.exchange_macaroons
    if app_name.startswith("snapcraft"):
        macaroon_response = "macaroon"
        authenticated_user_redirect = "store.index"
        exchange_macaroon_method = publisher_api.exchange_dashboard_macaroon
    return {
        "macaroon_response": macaroon_response,
        "user_redirect": authenticated_user_redirect,
        "exchange_macaroon_method": exchange_macaroon_method,
    }
