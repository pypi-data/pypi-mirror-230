import datetime
import re

import yaml

import talisker
from flask import make_response
from typing import List, Dict, TypedDict, Any

from canonicalwebteam.store_api.exceptions import StoreApiError

from canonicalwebteam.store_base.utils import helpers


Packages = TypedDict(
    "Packages_type",
    {
        "packages": List[
            Dict[str, Dict[str, str or List[str]] or List[Dict[str, str]]]
        ]
    },
)

Package = TypedDict(
    "Package_type",
    {
        "package": Dict[
            str, Dict[str, str or List[str]] or List[Dict[str, str]]
        ]
    },
)


def fetch_packages(store_api, fields: List[str], query) -> Packages:
    """
    Fetches packages from the store API based on the specified fields.

    :param: store_api: The specific store API object.
    :param: fields (List[str]): A list of fields to include in the package
    data.
    :param: query: A search query

    :returns: a dictionary containing the list of fetched packages.

    note: the response is cached for a maximum age of 3600 seconds.
    """
    store = store_api(talisker.requests.get_session())
    packages = store.find(fields=fields, query=query).get("results", [])
    response = make_response({"packages": packages})
    response.cache_control.max_age = 3600
    return response.json


def fetch_package(store_api, package_name: str, fields: List[str]) -> Package:
    """
    Fetches a package from the store API based on the specified package name.

    :param: store_api: The specific store API object.
    :param: package_name (str): The name of the package to fetch.
    :param: fields (List[str]): A list of fields to include in the package

    :returns: a dictionary containing the fetched package.
    """
    store = store_api(talisker.requests.get_session())
    package = store.get_item_details(
        name=package_name,
        fields=fields,
    )
    response = make_response({"package": package})
    response.cache_control.max_age = 3600
    return response.json


def get_bundle_charms(charm_apps):
    result = []

    if charm_apps:
        for app_name, data in charm_apps.items():
            # Charm names could be with the old prefix/suffix
            # Like: cs:~charmed-osm/mariadb-k8s-35
            name = data["charm"]
            if name.startswith("cs:") or name.startswith("ch:"):
                name = re.match(r"(?:cs:|ch:)(?:.+/)?(\S*?)(?:-\d+)?$", name)[
                    1
                ]

            charm = {"title": format_slug(name), "name": name}

            result.append(charm)

    return result


def parse_package_for_card(
    package: Dict[str, Any], store_name: str, store_api: Any
) -> Package:
    """
    Parses a package (snap, charm, or bundle) and returns the formatted package
    based on the given card schema.

    :param: package (Dict[str, Any]): The package to be parsed.
    :returns: a dictionary containing the formatted package.

    note:
        - This function has to be refactored to be more generic,
        so we won't have to check for the package type before parsing.

    """
    store = store_api(talisker.requests.get_session())
    resp = {
        "package": {
            "description": "",
            "display_name": "",
            "icon_url": "",
            "name": "",
            "platforms": [],
            "type": "",
        },
        "publisher": {"display_name": "", "name": "", "validation": ""},
        "categories": [],
        # hardcoded temporarily until we have this data from the API
        "ratings": {"value": "0", "count": "0"},
    }

    if store_name.startswith("charmhub"):
        result = package.get("result", {})
        publisher = result.get("publisher", {})

        resp["package"]["type"] = package.get("type", "")
        resp["package"]["name"] = package.get("name", "")
        resp["package"]["description"] = result.get("summary", "").split(".")[
            0
        ]
        resp["package"]["display_name"] = result.get(
            "title", format_slug(package.get("name", ""))
        )
        resp["publisher"]["display_name"] = publisher.get("display-name", "")
        resp["publisher"]["validation"] = publisher.get("validation", "")
        resp["categories"] = result.get("categories", [])
        resp["package"]["icon_url"] = helpers.get_icon(result.get("media", []))

        platforms = result.get("platforms", [])
        if platforms:
            resp["package"]["platforms"] = platforms
        else:
            resp["package"]["platforms"] = ["vm"]

        if resp["package"]["type"] == "bundle":
            name = package["name"]
            default_release = store.get_item_details(
                name, fields=["default-release"]
            )
            bundle_yaml = default_release["default-release"]["revision"][
                "bundle-yaml"
            ]

            bundle_details = yaml.load(bundle_yaml, Loader=yaml.FullLoader)
            bundle_charms = get_bundle_charms(
                bundle_details.get(
                    "applications", bundle_details.get("services", [])
                )
            )
            resp["charms"] = bundle_charms

    if store_name.startswith("snapcraft"):
        snap = package.get("snap", {})
        publisher = snap.get("publisher", {})
        resp["package"]["description"] = snap.get("summary", "").split(".")[0]
        resp["package"]["display_name"] = snap.get("title", "")
        resp["package"]["type"] = "snap"
        resp["package"]["name"] = package.get("name", "")
        # platform to be fetched
        resp["publisher"]["display_name"] = publisher.get("display-name", "")
        resp["publisher"]["name"] = publisher.get("username", "")
        resp["publisher"]["validation"] = publisher.get("validation", "")
        resp["categories"] = snap.get("categories", [])
        resp["package"]["icon_url"] = helpers.get_icon(
            package["snap"]["media"]
        )

    return resp


def paginate(
    packages: List[Packages], page: int, size: int, total_pages: int
) -> List[Packages]:
    """
    Paginates a list of packages based on the specified page and size.

    :param: packages (List[Packages]): The list of packages to paginate.
    :param: page (int): The current page number.
    :param: size (int): The number of packages to include in each page.
    :param: total_pages (int): The total number of pages.
    :returns: a list of paginated packages.

    note:
        - If the provided page exceeds the total number of pages, the last
        page will be returned.
        - If the provided page is less than 1, the first page will be returned.
    """

    if page > total_pages:
        page = total_pages
    if page < 1:
        page = 1

    start = (page - 1) * size
    end = start + size
    if end > len(packages):
        end = len(packages)

    return packages[start:end]


def get_packages(
    store,
    store_name: str,
    fields: List[str],
    size: int = 10,
    page: int = 1,
    query=None,
    filters: Dict = {},
) -> List[Dict[str, Any]]:
    """
    Retrieves a list of packages from the store based on the specified
    parameters.The returned packages are paginated and parsed using the
    card schema.

    :param: store: The store object.
    :param: fields (List[str]): A list of fields to include in the
            package data.
    :param: size (int, optional): The number of packages to include
            in each page. Defaults to 10.
    :param: page (int, optional): The current page number. Defaults to 1.
    :param: query (str, optional): The search query.
    :param: filters (Dict, optional): The filter parameters. Defaults to {}.
    :returns: a dictionary containing the list of parsed packages and
            the total pages
    """

    packages = fetch_packages(store, fields, query).get("packages", [])
    total_pages = -(len(packages) // -size)

    if filters:
        parsed_packages = []
        for package in packages:
            parsed_packages.append(
                parse_package_for_card(package, store_name, store)
            )
        filtered_packages = filter_packages(parsed_packages, filters)
        total_pages = -(len(filtered_packages) // -size)
        res = paginate(filtered_packages, page, size, total_pages)
    else:
        total_pages = -(len(packages) // -size)
        packages_per_page = paginate(packages, page, size, total_pages)
        parsed_packages = []
        for package in packages_per_page:
            parsed_packages.append(
                parse_package_for_card(package, store_name, store)
            )
        res = parsed_packages

    return {"packages": res, "total_pages": total_pages}


def filter_packages(
    packages: List[Packages], filter_params: Dict[str, List[str]]
):
    """
    Filters the list of packages based on the specified filter parameters.

    :param packages: the list of packages to filter.
    :param filter_params: The filter parameters
    :returns: the filtered list of packages.
    """

    result = packages
    for key, val in filter_params.items():
        if key == "categories" and "all" not in val:
            result = list(
                filter(
                    lambda package: len(
                        [
                            cat
                            for cat in package["categories"]
                            if cat["name"] in val
                        ]
                    )
                    != 0,
                    result,
                )
            )
        if (key == "platforms" or key == "architectures") and "all" not in val:
            platform = "platforms" if key == "platforms" else "architectures"
            result = list(
                filter(
                    lambda package: len(
                        [p for p in package["package"][platform] if p in val]
                    )
                    != 0,
                    result,
                )
            )

        if key == "type" and "all" not in val:
            result = list(
                filter(
                    lambda package: package["package"]["type"] in val, result
                )
            )

    return result


def format_slug(slug):
    """Format category name into a standard title format

    :param slug: The hypen spaced, lowercase slug to be formatted
    :return: The formatted string
    """
    return (
        slug.title()
        .replace("-", " ")
        .replace("And", "and")
        .replace("Iot", "IoT")
    )


def parse_categories(
    categories_json: Dict[str, List[Dict[str, str]]]
) -> List[Dict[str, str]]:
    """
    :param categories_json: The returned json from store_api.get_categories()
    :returns: A list of categories in the format:
    [{"name": "Category", "slug": "category"}]
    """

    categories = []

    if "categories" in categories_json:
        for category in categories_json["categories"]:
            categories.append(
                {"slug": category, "name": format_slug(category)}
            )

    return categories


def get_store_categories(store_api) -> List[Dict[str, str]]:
    """
    Fetches all store categories.

    :param: store_api: The store API object used to fetch the categories.
    :returns: A list of categories in the format:
    [{"name": "Category", "slug": "category"}]
    """
    store = store_api(talisker.requests.get_session())
    try:
        all_categories = store.get_categories()
    except StoreApiError:
        all_categories = []

    return all_categories


def get_snaps_account_info(account_info):
    """Get snaps from the account information of a user

    :param account_info: The account informations

    :return: A list of snaps
    :return: A list of registred snaps
    """
    user_snaps = {}
    registered_snaps = {}
    if "16" in account_info["snaps"]:
        snaps = account_info["snaps"]["16"]
        for snap in snaps.keys():
            if snaps[snap]["status"] != "Revoked":
                if not snaps[snap]["latest_revisions"]:
                    registered_snaps[snap] = snaps[snap]
                else:
                    user_snaps[snap] = snaps[snap]

    now = datetime.datetime.utcnow()

    for snap in user_snaps:
        snap_info = user_snaps[snap]
        for revision in snap_info["latest_revisions"]:
            if len(revision["channels"]) > 0:
                snap_info["latest_release"] = revision
                break

    if len(user_snaps) == 1:
        for snap in user_snaps:
            snap_info = user_snaps[snap]
            revisions = snap_info["latest_revisions"]

            revision_since = datetime.datetime.strptime(
                revisions[-1]["since"], "%Y-%m-%dT%H:%M:%SZ"
            )

            if abs((revision_since - now).days) < 30 and (
                not revisions[0]["channels"]
                or revisions[0]["channels"][0] == "edge"
            ):
                snap_info["is_new"] = True

    return user_snaps, registered_snaps


def get_package(
    store, store_name: str, package_name: str, fields: List[str]
) -> Package:
    """Get a package by name

    :param store: The store object.
    :param store_name: The name of the store.
    :param package_name: The name of the package.
    :param fields: The fields to fetch.

    :return: A dictionary containing the package.
    """
    package = fetch_package(store, package_name, fields).get("package", {})

    return {"package": parse_package_for_card(package, store_name, store)}
