#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any

import requests

from cr_api_client.config import cr_api_client_config

# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: str) -> requests.Response:
    return requests.get(
        f"{cr_api_client_config.scenario_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _post(route: str, **kwargs: str) -> requests.Response:
    return requests.post(
        f"{cr_api_client_config.scenario_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _put(route: str, **kwargs: str) -> requests.Response:
    return requests.put(
        f"{cr_api_client_config.scenario_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _delete(route: str, **kwargs: str) -> requests.Response:
    return requests.delete(
        f"{cr_api_client_config.scenario_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _handle_error(
    result: requests.Response, context_error_msg: str
) -> requests.Response:
    if (
        result.headers.get("content-type") == "application/json"
        and "message" in result.json()
    ):
        error_msg = result.json()["message"]
    else:
        error_msg = result.text

    raise Exception(
        f"{context_error_msg}. "
        f"Status code: '{result.status_code}'.\n"
        f"Error message: '{error_msg}'."
    )


# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def get_version() -> str:
    """
    Return publish API version.

    :return: The version number is a string
    """
    result = _get("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve scenario API version")

    return result.json()


# -------------------------------------------------------------------------- #
# Scenario API
# -------------------------------------------------------------------------- #


def fetch_unit_attacks() -> Any:
    """
    List all available unit attacks

    :return: the JSON list of unit attacks
    """
    result = _get("/unit_attack")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve unit attacks from scenario API")

    return result.json()


def fetch_unit_attack_by_id(unit_attack_id: str) -> Any:
    """
    Get the full JSON manifest of a specific unit attack

    :param unit_attack_id: id of the unit attack to fetch

    :return: the JSON of unit attacks
    """
    result = _get(f"/unit_attack/{unit_attack_id}")

    if result.status_code != 200:
        _handle_error(
            result,
            f"Cannot retrieve unit attack {unit_attack_id} from frontend publish API",
        )

    return result.json()


def fetch_scenarios() -> Any:
    """
    List all available scenarios

    :return: the JSON list of unit attacks
    """
    result = _get("/scenario")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve scenarios from scenario API")

    return result.json()


def fetch_scenario_by_title(scenario_id: str) -> Any:
    """
    Get the full JSON manifest of a specific scenario

    :param unit_attack_id: id of the unit attack to fetch

    :return: the JSON of unit attacks
    """
    result = _get(f"/scenario/{scenario_id}")

    if result.status_code != 200:
        _handle_error(
            result, f"Cannot retrieve scenario {scenario_id} from scenario API"
        )

    return result.json()
