from flask import Blueprint

sample_bp = Blueprint(
    "test_store_bp",
    __name__,
)


@sample_bp.route("/test_store_bp")
def sample_route():
    return "This is a test blueprint on the storebase"
