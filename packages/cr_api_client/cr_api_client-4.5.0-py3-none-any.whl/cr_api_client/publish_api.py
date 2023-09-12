#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from typing import Any
from uuid import UUID

import requests

from cr_api_client.config import cr_api_client_config

# -------------------------------------------------------------------------- #
# Internal helpers
# -------------------------------------------------------------------------- #


def _get(route: str, **kwargs: str) -> requests.Response:
    return requests.get(
        f"{cr_api_client_config.publish_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _post(route: str, **kwargs: str) -> requests.Response:
    return requests.post(
        f"{cr_api_client_config.publish_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _put(route: str, **kwargs: str) -> requests.Response:
    return requests.put(
        f"{cr_api_client_config.publish_api_url}{route}",
        verify=cr_api_client_config.cacert,
        cert=(cr_api_client_config.cert, cr_api_client_config.key),
        timeout=30,
        **kwargs,
    )


def _delete(route: str, **kwargs: str) -> requests.Response:
    return requests.delete(
        f"{cr_api_client_config.publish_api_url}{route}",
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

    :return: The version inumber n a string
    """
    result = _get("/version")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve publish frontend API version")

    return result.json()


# -------------------------------------------------------------------------- #
# Publish Frontend API
# -------------------------------------------------------------------------- #


def fetch_datasets() -> Any:
    """
    List all available datasets

    :return: the JSON list of manifests
    """
    result = _get("/")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve datasets from frontend publish API")

    return result.json()


def fetch_dataset_by_uuid(partial_dataset_id: str) -> Any:
    """
    Get the full JSON manifest of a specific dataset

    :param partial_dataset_id: UUID of the dataset to fetch, or prefix of it that uniquely identifies the dataset

    If a full UUID is given, returns the identified dataset metadata if it
    exists. If a partial UUID (prefix of an existing UUID) is given, and this
    prefix uniquely identifies one and only one dataset, the latter's metadata
    is returned.
    """
    result = _get(f"/{partial_dataset_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve dataset from frontend publish API")

    return result.json()


def fetch_dataset_resource(
    partial_dataset_id: str, resource_type_str: str, resource_id: UUID
) -> Any:
    """
    Get the description of a specific resource.

    This function *does not* fetch the file(s) associated with one resource,
    it merely returns the portion of the JSON manifest that describes that
    particular resource. This JSON includes, in particular, the list
    of files included in the resource, and the URLs to download them. It is
    up to the user to manually fetch these URLs.

    :param partial_dataset_id: UUID of the dataset to which the resource belongs, or a prefix of it that uniquely identifies it
    :param resource_type_str: type of the resource to fetch. Must be a string among "log", "pcap", "memory_dump", "redteam_report", "life_report"
    :param resource_id: UUID of the resource
    :return: JSON structure describing the resource
    """
    result = _get(f"/{partial_dataset_id}/{resource_type_str}/{resource_id}")

    if result.status_code != 200:
        _handle_error(result, "Cannot retrieve dataset from frontend publish API")

    return result.json()


def delete_dataset(
    dataset_id: str, delete_remote_data: bool = True, force: bool = False
) -> None:
    """
    Delete a specific dataset

    :param dataset_id: the full UUID of the dataset to delete
    :param delete_remote_data: (optional, default True) if True  all data related to the datasets (locally or remotely stored) is deleted; otherwise, only local data and the manifest of erach dataset are removed.
    :param force: (optional, default False) if True, forces the deletion of the dataset, even if there are validation errors in the manifest, or in the dataset contents. If the manifest is corrupted, remotely stored resources may not be deleted even though delete_remote_data was set to True.

    """
    result = _delete(
        f"/{dataset_id}",
        params={"delete_remote_data": delete_remote_data, "force": force},
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot delete dataset from frontend publish API")

    return None


def delete_all_datasets(delete_remote_data: bool = True, force: bool = False) -> Any:
    """
    Delete all datasets

    :param delete_remote_data: (optional, default True) if True  all data related to the datasets (locally or remotely stored) is deleted; otherwise, only local data and the manifest of erach dataset are removed.
    :param force: (optional, default False) if True, forces the deletion of the datasets, even if there are validation errors in the manifests, or in the datasets contents. If a manifest is corrupted, remotely stored resources for that dataset may not be deleted even though delete_remote_data was set to True.
    :return: a JSON structure specifying the datasets that were successfully deleted, and the errors encountered

    """

    result = _delete(
        "/all", params={"delete_remote_data": delete_remote_data, "force": force}
    )

    if result.status_code != 200:
        _handle_error(result, "Cannot delete datasets from frontend publish API")

    return result.json()
