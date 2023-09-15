import os

from canonicalwebteam.store_api.stores.charmstore import (
    CharmStore,
    CharmPublisher,
)
from canonicalwebteam.store_api.stores.snapstore import (
    SnapStore,
    SnapPublisher,
)

ENVIRONMENT = os.getenv("ENVIRONMENT", "devel")
SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")

# we want to ensure the keys matches the app name for each store for now
PACKAGE_PARAMS = {
    "snapcraft_beta": {
        "store": SnapStore,
        "publisher": SnapPublisher,
        "fields": [
            "title",
            "summary",
            "media",
            "publisher",
            "categories",
        ],
        "size": 15,
    },
    "charmhub_beta": {
        "store": CharmStore,
        "publisher": CharmPublisher,
        "fields": [
            "result.categories",
            "result.summary",
            "result.media",
            "result.title",
            "result.publisher.display-name",
            "default-release.revision.revision",
            "default-release.channel",
            "result.deployable-on",
        ],
        "size": 12,
    },
}
