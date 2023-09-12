"""Function for search.

    Typical example usage:

    import tonita
    from tonita.datatypes.search import SearchRequest

    # Option 1: Set an API key and corpus ID to use for subsequent calls. These 
    # will be overridden if specified in the call itself. If the environment
    # variable `TONITA_API_KEY` is set, `tonita.api_key` will already be equal 
    # to that value.
    tonita.api_key = "my-api-key"
    tonita.corpus_id = "my-corpus-id"

    request = SearchRequest(
        query="this is a query", 
        max_results=10,
        categories=["x", "y"]
    )

    tonita.search(request=request)

    # Option 2: Specify the API key and corpus ID in the API call. This will 
    # override the value of both `tonita.api_key` and `tonita.corpus_id`.
    tonita.search(
        request=request,
        api_key="another-api_key",
        corpus_id="another-corpus-id"
    )
"""

import requests
from dataclasses import asdict
from typing import Optional

from tonita.api.helpers import (
    _get_module_var_value,
    _request,
    _resolve_field_value,
)
from tonita.constants import (
    CORPUS_ID_HTTP_HEADER_FIELD_NAME,
    CORPUS_ID_NAME,
    HTTP_METHOD_POST,
    SEARCH_PATH_ROOT_NAME,
)
from tonita.datatypes.search import (
    SearchRequest,
    SearchResponse,
    SearchResponseItem,
    Snippet,
)

# Defaults to "search" unless set manually by the user in the environment.
SEARCH_PATH_ROOT = _get_module_var_value(SEARCH_PATH_ROOT_NAME)


def search(
    request: SearchRequest,
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
    session: Optional[requests.Session] = None,
) -> SearchResponse:
    """Return search results given a query.

    Args:
        request (SearchRequest):
            See docstring for datatypes.search.SearchRequest.

        corpus_id (Optional[str]):
            The ID of the corpus to search within. If this argument is `None`,
            then the value of `tonita.corpus_id` will be used.

        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

        session (Optional[requests.Session]):
            A `requests.Session` object to use for the request. If
            the user does not provide a session, a new one will be created.

    Returns:
        SearchResponse:
            See docstring for `datatypes.search.SearchResponse`.

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
        url_path=SEARCH_PATH_ROOT,
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data=asdict(request),
        session=session,
    )

    search_response_items = []
    for item in response["items"]:
        # Pack snippets.
        snippets = []
        for snippet in item["snippets"]:
            snippets.append(Snippet(display_string=snippet["display_string"]))

        search_response_items.append(
            SearchResponseItem(
                listing_id=item["listing_id"],
                score=item["score"],
                categories=item["categories"],
                snippets=snippets,
            )
        )

    return SearchResponse(items=search_response_items)
