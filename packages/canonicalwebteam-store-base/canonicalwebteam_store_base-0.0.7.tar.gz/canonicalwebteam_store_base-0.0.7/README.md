# Canonical Webteam Store-base

## About

This is the base application for all stores. Each store is registered as a blueprint when the app is initialized, other configs and blueprints that are store-specific are also registered on the app. This allows for uniformity of certain endpoints and functionalities across all stores and also allows for extension and customization of endpoints and features that are store specific. See Usage section for example.

## How to Install
To install this extension as a requirement in your project, you can use PIP:
`pip install canonicalwebteam.store-base`

## Development

The package leverages poetry for dependency management.

## Testing

All tests can be run with `poetry run python3 -m unittest discover tests`.

Note: You might have to do `poetry install` before running the command above.

## Usage

```
from canonicalwebteam.store_base.app import create_app

import store-specific blueprint
import store-specific utility processor

app = create_app(
    "app_name",
    store_bp=store-specific blueprint,
    utility_processor=store-specific utility_processor,
)

app.static_folder=app_static_folder
app.template_folder=app_template_folder
app.static_url_path=app_static_url_path

all other store blueprints and configurations should be registered here

```