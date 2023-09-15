import flask

import re
import json
import os

from bs4 import BeautifulSoup
from canonicalwebteam.discourse import DiscourseAPI
from flask import request
from ruamel.yaml import YAML
from slugify import slugify
from talisker import requests


session = requests.get_session()
discourse_api = DiscourseAPI(
    base_url="https://discourse.charmhub.io/",
    session=session,
)

_yaml = YAML(typ="rt")
_yaml_safe = YAML(typ="safe")


def get_soup(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup


def get_yaml_loader(typ="safe"):
    if typ == "safe":
        return _yaml_safe
    return _yaml


def get_yaml(filename, typ="safe", replaces={}):
    """
    Reads a file, replaces occurences of all the keys in `replaces` with the
    correspondant values and returns an ordered dict with the YAML content

    Keyword arguments:
    filename -- name if the file to load.
    typ -- type of yaml loader
    replaces -- key/values to replace in the file content (default {})
    """
    try:
        yaml = get_yaml_loader(typ)
        data = get_file(filename, replaces)
        return yaml.load(data)
    except Exception:
        return None


def dump_yaml(data, stream, typ="safe"):
    yaml = get_yaml_loader(typ)
    yaml.dump(data, stream)


def get_icon(media):
    icons = [m["url"] for m in media if m["type"] == "icon"]
    if len(icons) > 0:
        return icons[0]
    return ""


def get_file(filename, replaces={}):
    """
    Reads a file, replaces occurences of all the keys in `replaces` with
    the correspondant values and returns the resulting string or None

    Keyword arguments:
    filename -- name if the file to load.
    replaces -- key/values to replace in the file content (default {})
    """
    filepath = os.path.join(flask.current_app.root_path, filename)

    try:
        with open(filepath, "r") as f:
            data = f.read()
            for key in replaces:
                data = data.replace(key, replaces[key])
    except Exception:
        data = None

    return data


def get_licenses():
    """
    Retrieves the list of licenses from a JSON file.

    :returns: The list of licenses, where each license is represented as a
    dictionary with "licenseId" and "name" keys.
    """

    try:
        with open("licenses.json") as f:
            licenses = json.load(f)["licenses"]

        def _build_custom_license(license_id, license_name):
            return {"licenseId": license_id, "name": license_name}

        CUSTOM_LICENSES = [
            _build_custom_license("Proprietary", "Proprietary"),
            _build_custom_license("Other Open Source", "Other Open Source"),
            _build_custom_license(
                "AGPL-3.0+", "GNU Affero General Public License v3.0 or later"
            ),
        ]

        licenses = licenses + CUSTOM_LICENSES
    except Exception:
        licenses = []

    return licenses


# Change all the headers (if step=2: eg h1 => h3)
def decrease_header(header, step):
    level = int(header.name[1:]) + step
    if level > 6:
        level = 6
    header.name = f"h{str(level)}"

    return header


def add_header_id(h, levels):
    """
    :param h(tag): The HTML header element.
    :param levels(list): The list of previous header levels and their
    corresponding IDs.

    :returns: The modified HTML header element with the added ID attribute.
    """
    id = slugify(h.get_text())
    level = int(h.name[1:])

    # Go through previous headings and find any that are lower
    levels.append((level, id))
    reversed_levels = list(reversed(levels))
    parents = []
    level_cache = None
    for i in reversed_levels:
        if i[0] < level and not level_cache:
            parents.append(i)
            level_cache = i[0]
        elif i[0] < level and i[0] < level_cache:
            parents.append(i)
            level_cache = i[0]
    parents.reverse()
    if "id" not in h.attrs:
        parent_path_id = ""
        if len(parents) > 0:
            parent_path_id = "--".join([i[1] for i in parents]) + "--"
        h["id"] = parent_path_id + id

    return h


def modify_headers(soup, decrease_step=2):
    levels = []

    for header in soup.find_all(re.compile("^h[1-6]$")):
        decrease_header(header, decrease_step)
        add_header_id(header, levels)

    return soup


def is_safe_url(url):
    """
    Check if the URL is safe within the context of the current app.

    :param url(str): The URL to check.
    :returns: True if the URL is safe, False otherwise.
    """
    return url.startswith(request.url_root) or url.startswith("/")
