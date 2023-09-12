"""Functions for listing-related operations.

    Typical example usage:

    import tonita

    # We first add a listing using an in-memory dict.

    # Option 1: Set an API key and corpus ID to use for subsequent calls. These 
    # will be overridden if specified in the call itself. If the environment
    # variable `TONITA_API_KEY` is set, `tonita.api_key` will already be equal 
    # to that value.
    tonita.api_key = "my-api-key"
    tonita.corpus_id = "my-corpus-id"

    tonita.listings.add(data=data)

    # Option 2: Specify the API key in the API call. This will override the
    # value of both `tonita.api_key` and `tonita.corpus_id`.
    tonita.listings.add(
        data=data, 
        corpus_id="another-corpus-id", 
        api_key="another-api-key"
    )

    # We can also add a listing using a file. Since `api_key` and `corpus_id`
    # are not specified in this call, this call will use the values of
    # `tonita.api_key` and `tonita.corpus_id`.
    tonita.listings.add(json_path="path/to/file.json")

    # List all available listing IDs.
    tonita.listings.list(limit=-1)

    # Get data for a single listing.
    tonita.listings.get(listing_ids=["listing_id_1"])

    # Get data for multiple listings.
    tonita.listings.get(listing_ids=["listing_id_1", "listing_id_2"])

    # Delete a single listing.
    tonita.listings.delete(listing_ids=["listing_id_1"])

    # Delete multiple listings.
    tonita.listings.delete(listing_ids=["listing_id_2", "listing_id_3"])
"""

import requests
from typing import Any, Dict, List, Optional

from tonita.api.helpers import (
    _get_module_var_value,
    _request,
    _resolve_field_value,
)
from tonita.constants import (
    CORPUS_ID_HTTP_HEADER_FIELD_NAME,
    CORPUS_ID_NAME,
    HTTP_METHOD_POST,
    LISTINGS_PATH_ROOT_NAME,
)
from tonita.datatypes.listings import (
    AddListingsResponse,
    AddSingleListingResult,
    DeleteListingsResponse,
    DeleteSingleListingResult,
    GetListingsResponse,
    GetSingleListingResult,
    ListListingsResponse,
    RecoverListingsResponse,
    RecoverSingleListingResult,
    State,
)

# Defaults to "listings" unless set manually by the user in the environment.
LISTINGS_PATH_ROOT = _get_module_var_value(LISTINGS_PATH_ROOT_NAME)


def add(
    data: Optional[Dict[str, Any]] = None,
    json_path: Optional[str] = None,
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[requests.Session] = None,
) -> AddListingsResponse:
    """Add (or overwrite if already exists) data for a batch of listings.

    This method allows for adding listings data to Tonita's service (or
    updating if a listing was previously added) through two means:
        1. as a dict passed to the `data` parameter, or
        2. as a JSON file whose path is passed to the `json_path` parameter.

    Exactly one of `data` or `json_path` should be provided. If both or neither
    are provided, an error will be thrown.

    If a listing ID is found to already exist on Tonita's server, THE PREVIOUS
    DATA FOR THAT LISTING WILL BE OVERWRITTEN.

    The value passed to `data` must be a dict formatted as follows:

        Each key should be a string for the ID of the listing. The value
        associated with a particular key should itself be a dict with two
        keys: "data" or "categories".

            - The "data" key will map to a dict that stores facet data for
                a listing as key-value pairs. For example, one facet of a
                movie might be "genre", which will be the key. The value of
                that key might be "drama", in which case an entry of this
                "data" dict will be `"genre": "drama"`.

                A value for this "data" key is required.

            - The "categories" key will map to a list of strings that
                denote the set of categories this listing falls under.

                This key is optional but recommended.

            Example:

            {
                "listing1": {
                    "data": {"Bd": 2, "Br": 1, "address": "123 Foo St."},
                    "categories": ["Apartments/New York"],
                },
                "listing2": {
                    "data": {"Bd": 3, "Br": 2, "address": "456 Bar St."},
                    "categories": [
                        "Homes/Town Homes/San Jose",
                        "Homes/Co-ops/San Jose"
                    ],
                },
            }

    The contents of the file located at `json_path` will be expected to be in
    the same form.

    Args:
        data (Optional[Dict[str, Any]]):
            A dict containing listings data.
            Exactly one of `data` or `json_path` should be provided.
        json_path (Optional[str]):
            A path to a JSON file containing listings data.
            Exactly one of `data` or `json_path` should be provided.
        corpus_id (Optional[str]):
            The ID of the corpus this listing belongs to. If this argument is
            `None`, then the value of `tonita.corpus_id` will be used.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.
        session (Optional[requests.Session]):
            A `requests.Session` object to use for the request. If
            the user does not provide a session, a new one will be created.

    Returns:
        AddListingsResponse:
            See docstring for `datatypes.listings.AddListingsResponse`.

    Raises:
        TonitaBadRequestError:
            The request is malformed; see error message for specifics.
        TonitaInternalServerError:
            A server-side error occurred.
        TonitaUnauthorizedError:
            The API key is missing or invalid.
        ValueError:
            - If neither `data` nor `json_path` are provided.
            - If both `data` and `json_path` are provided.
    """

    response = _request(
        method=HTTP_METHOD_POST,
        url_path=f"{LISTINGS_PATH_ROOT}/add",
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data=data,
        json_path=json_path,
        session=session,
    )

    response = AddListingsResponse(**response)

    # Cast each item of `response.results` from dict to dataclass.
    for listing_id, listing_result in response.results.items():
        response.results[listing_id] = AddSingleListingResult(**listing_result)

    return response


def list(
    start_listing_id: Optional[str] = None,
    limit: int = 1000,
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> ListListingsResponse:
    """List IDs of all listings in corpus given by `corpus_id`.

    This method allows for "pagination" through listing IDs via sequential
    calls. For example, suppose we want to retrieve all listing IDs for a given
    corpus with ID "my-corpus-id", but we don't want to return more than 29 IDs
    at a time. We can make the following calls:

        tonita.api_key = "my-api-key"
        tonita.corpus_id = "my-corpus_id"

        num_results_limit = 29

        # The default for `start_listing_id` is `None`.
        response = tonita.listings.list(limit=num_results_limit)

        # Do something with the first 29 listing IDs.
        do_something(response.results)

        # Do something with the rest of the listing IDs.
        while response.next_listing_id is not None:
            response = tonita.listings.list(
                start_listing_id=response.next_listing_id,
                limit=num_results_limit
            )

            do_something(response.results)

    Args:
        start_listing_id (Optional[str]):
            If provided, then only listings whose IDs appear at or after this
            listing ID according to lexicographical order are returned. If
            `None`, then listing IDs are returned beginning with the first
            listing ID according to lexicographical order.
        limit (int):
            If provided, then at most this many listing IDs are returned (in
            lexicographical order). The default returns at most 1000 listing
            IDs. To return all listing IDs in the corpus, pass -1. If there are
            more listing IDs to return than a positive `limit`, then the
            `next_listing_id` field in the return object will be populated with
            the next listing ID according to lexicographical order. The caller
            can pass this listing ID as `start_listing_id` in a subsequent call
            to `list()` to "page" through the remaining results. If there are
            no more listing IDs to return, the `next_listing_id` field in the
            response will be `None`.
        corpus_id (Optional[str]):
            The ID of the corpus this listing belongs to. If this argument is
            `None`, then the value of `tonita.corpus_id` will be used.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        ListListingsResponse:
            See docstring for `datatypes.listings.ListListingsResponse`.

    Raises:
        TonitaBadRequestError:
            The request is malformed; see error message for specifics.
        TonitaInternalServerError:
            A server-side error occurred.
        TonitaUnauthorizedError:
            The API key is missing or invalid.
    """

    response = _request(
        method=HTTP_METHOD_POST,
        url_path=f"{LISTINGS_PATH_ROOT}/list",
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data={"start_listing_id": start_listing_id, "limit": limit},
    )

    response = ListListingsResponse(**response)

    for listing_id, state in response.results.items():
        response.results[listing_id] = State(state)

    return response


def get(
    listing_ids: List[str],
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> GetListingsResponse:
    """Retrieve data for specified listings.

    Args:
        listing_ids (List[str]):
            The IDs of the listings to retrieve. The elements of this list must
            be distinct (i.e., no duplicates); a `TonitaBadRequestError` will
            be raised otherwise.
        corpus_id (Optional[str]):
            The ID of the corpus this listing belongs to. If this argument is
            `None`, then the value of `tonita.corpus_id` will be used.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        GetListingsResponse:
            See docstring for `datatypes.listings.GetListingsResponse`.

    Raises:
        TonitaBadRequestError:
            The request is malformed; see error message for specifics.
        TonitaInternalServerError:
            A server-side error occurred.
        TonitaUnauthorizedError:
            The API key is missing or invalid.
    """

    response = _request(
        method=HTTP_METHOD_POST,
        url_path=f"{LISTINGS_PATH_ROOT}/get",
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data={"listing_ids": listing_ids},
    )

    response = GetListingsResponse(**response)

    for listing_id, listing_result in response.results.items():
        # Cast each item of `response.results` from dict to dataclass.
        response.results[listing_id] = GetSingleListingResult(**listing_result)

        # Cast state value to `State` enum or `None`.
        state = None
        if response.results[listing_id].state is not None:
            state = State(response.results[listing_id].state)
        response.results[listing_id].state = state

    return response


def delete(
    listing_ids: List[str],
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> DeleteListingsResponse:
    """Delete data for listings.

    This method technically only "marks" listings to be deleted after some
    period of time. Until then, the user can still recover a listing by calling
    `recover()`.

    After a sufficiently long time has elapsed, deleted listings can no longer
    be recovered. To check how much time is left before a listing expires, call
    `listings.get()` and check the `seconds_to_expiration` field in the
    response.

    Args:
        listing_ids (List[str]):
            The IDs of the listings to delete. The elements of this list must
            be distinct (i.e., no duplicates); a `TonitaBadRequestError` will
            be raised otherwise.
        corpus_id (Optional[str]):
            The ID of the corpus this listing belongs to. If this argument is
            `None`, then the value of `tonita.corpus_id` will be used.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        DeleteListingsResponse:
            See docstring for `datatypes.DeleteListingsResponse`.

    Raises:
        TonitaBadRequestError:
            The request is malformed; see error message for specifics.
        TonitaInternalServerError:
            A server-side error occurred.
        TonitaUnauthorizedError:
            The API key is missing or invalid.
    """

    response = _request(
        method=HTTP_METHOD_POST,
        url_path=f"{LISTINGS_PATH_ROOT}/delete",
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data={"listing_ids": listing_ids},
    )

    response = DeleteListingsResponse(**response)

    # Cast each item of `response.results` from dict to dataclass.
    for listing_id, listing_result in response.results.items():
        response.results[listing_id] = DeleteSingleListingResult(
            **listing_result
        )

    return response


def recover(
    listing_ids: List[str],
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> RecoverListingsResponse:
    """Recover a batch of listings that were previously marked to be deleted.

    Args:
        listing_ids (List[str]):
            The IDs of the listings to recover. The elements of this list must
            be distinct (i.e., no duplicates); a `TonitaBadRequestError` will
            be raised otherwise.
        corpus_id (Optional[str]):
            The ID of the corpus this listing belongs to. If this argument is
            `None`, then the value of `tonita.corpus_id` will be used.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        RecoverListingsResponse:
            See docstring for `datatypes.corpora.RecoverListingsResponse`.

    Raises:
        TonitaBadRequestError: The request is malformed; see error message for
            specifics.
        TonitaInternalServerError: A server-side error occurred.
        TonitaUnauthorizedError: The API key is missing or invalid.
    """

    response = _request(
        method=HTTP_METHOD_POST,
        url_path=f"{LISTINGS_PATH_ROOT}/recover",
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data={"listing_ids": listing_ids},
    )

    response = RecoverListingsResponse(**response)

    # Cast each item of `response.results` from dict to dataclass.
    for listing_id, listing_result in response.results.items():
        response.results[listing_id] = RecoverSingleListingResult(
            **listing_result
        )

    return response
