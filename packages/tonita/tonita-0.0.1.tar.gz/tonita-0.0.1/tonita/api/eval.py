"""Functions for evaluation-related operations.

    Typical example usage:

    First, submit a batch of search requests for evaluation.
    ```
    import tonita
    from tonita.datatypes.search import SearchRequest
    from tonita.datatypes.eval import EvalStatus

    # Option 1: Set an API key and corpus ID to use for subsequent calls. These 
    # will be overridden if specified in the call itself. If the environment
    # variable `TONITA_API_KEY` is set, `tonita.api_key` will already be equal 
    # to that value.
    tonita.api_key = "my-api-key"
    tonita.corpus_id = "my-corpus-id"


    # Create a list of search requests to evaluate and submit.
    requests_a = [
        SearchRequest(
            query="this is the first query",
            categories=["x", "y"],
        ),
        SearchRequest(
            query="this is another query", categories=["x"]
        ),
        SearchRequest(
            query="i want to evaluate all of these",
            categories=["a", "b", "c"],
        ),
    ]

    # Receive a `tonita.datatypes.search.SubmitEvalResponse`.
    submission_a = tonita.eval.submit(
        search_requests=requests_a,
        notification_email_addresses=["a@abc.io", "b@def.co"]
    )

    # Option 2: Specify the API key and corpus ID in the API call. This will 
    # override the value of both `tonita.api_key` and `tonita.corpus_id`.
    requests_b = [
        SearchRequest(
            query="here is another batch",
            categories=["z"],
        ),
        SearchRequest(
            query="i also want to evaluate these"
        ),
    ]

    # Receive a `tonita.datatypes.search.SubmitEvalResponse`.
    submission_b = tonita.eval.submit(
        search_requests=requests_b,
        notification_email_addresses=[c@ghi.com]
        corpus_id="another-corpus-id", 
        api_key="another-api-key"
    )
    ```

    Once an evaluation is submitted, some time is needed for the evaluation to
    complete. We provide a `retrieve()` method that allows developers to check
    the progress of their evaluation and, once sufficiently many queries in the
    batch are complete, to retrieve the results of the evaluation. 
    
    Developers will be notified at the email addresses provided during
    submission when results are ready for retrieval.

    ```
    import tonita
    from tonita.datatypes.search import SearchRequest
    from tonita.datatypes.eval import EvalStatus

    # Suppose that `eval_id_a` contains the value of `submission_a.eval_id`.

    # Check the status of the evaluation/retrieve its response.
    retrieve_response = tonita.eval.retrieve(
        eval_id=eval_id_a,
        corpus_id="my-corpus-id",
        api_key="my-api-key"
    )

    if retrieve_response.status is in [
        EvalStatus.SUBMITTED, EvalStatus.IN_PROGRESS
    ]:
        print("Evaluation in progress... please try again later.")
        ...
    elif: retrieval.status is EvalStatus.COMPLETED:
        # Do something with results.
        ...
    else:
        # Otherwise handle the error returned.
    ```
"""
import warnings
from dataclasses import asdict
from typing import List, Optional

from tonita.api.helpers import (
    _get_module_var_value,
    _request,
    _resolve_field_value,
)
from tonita.constants import (
    CORPUS_ID_HTTP_HEADER_FIELD_NAME,
    CORPUS_ID_NAME,
    EVAL_PATH_ROOT_NAME,
    HTTP_METHOD_POST,
)
from tonita.datatypes.eval import (
    EvalStatus,
    ListingResult,
    Metrics,
    QueryResult,
    RetrieveEvalResponse,
    SubmitEvalRequest,
    SubmitEvalResponse,
)
from tonita.datatypes.search import SearchRequest
from tonita.errors import TonitaBadRequestError

# Defaults to "eval" unless set manually by the user in the environment.
EVAL_PATH_ROOT = _get_module_var_value(EVAL_PATH_ROOT_NAME)


def submit(
    search_requests: List[SearchRequest],
    notification_email_addresses: List[str],
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> SubmitEvalResponse:
    """Submits a request for evaluation of a batch of search requests.

    The evaluation process is asynchronous. That is, evaluation of a given
    search request requires time to process, and results are not available
    immediately. Therefore, the return value of this function is not the
    evaluation result, but an ID for the evaluation. The developer can then
    pass that ID to `retrieve()` to check the status of the evaluation and to
    retrieve the results of a completed evaluation when available.

    Args:
        search_requests (List[SearchRequest]):
            A list of `SearchRequest`s to evaluate. See docstring for
            `datatypes.search.SearchRequest`.

        notification_email_addresses (List[str]):
            A list of email addresses to which notifications about the progress
            of this evaluation should be sent.

        corpus_id (Optional[str]):
            The ID of the corpus to search within for this batch of search
            requests. If this argument is `None`, then the value of
            `tonita.corpus_id` will be used.

        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        SubmitEvalResponse:
            See docstring for `datatypes.eval.SubmitEvalResponse`.

    Raises:
        TonitaBadRequestError:
            The request is malformed; see error message for specifics.
        TonitaInternalServerError:
            A server-side error occurred.
        TonitaUnauthorizedError:
            The API key is missing or invalid.
    """

    warnings.warn(
        "In evaluation, the value of `max_results` for `SearchRequests` will "
        "be ignored."
    )

    request = SubmitEvalRequest(
        email_addresses=notification_email_addresses,
        search_requests=search_requests,
    )

    response = _request(
        method=HTTP_METHOD_POST,
        url_path=f"{EVAL_PATH_ROOT}/submit",
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data=asdict(request),
    )

    return SubmitEvalResponse(**response)


def retrieve(
    eval_id: str,
    corpus_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> RetrieveEvalResponse:
    """Retrieves the status of an evaluation, as well as results if available.

    Args:
        eval_id (str):
            The ID of an evaluation whose status to check or results to
            retrieve.

        corpus_id (Optional[str]):
            The ID of the corpus that was used when submitting the evaluation.
            If this argument is `None`, then the value of `tonita.corpus_id`
            will be used.

        api_key (Optional[str]):
            An API key corresponding to the submitted evaluation. If this
            argument is `None`, then the value of `tonita.api_key` will be
            used.

    Returns:
        RetrieveEvalResponse:
            See docstring for datatypes.eval.RetrieveEvalResponse.

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
        url_path=f"{EVAL_PATH_ROOT}/retrieve",
        headers={
            CORPUS_ID_HTTP_HEADER_FIELD_NAME: _resolve_field_value(
                name=CORPUS_ID_NAME, value=corpus_id
            )
        },
        api_key=api_key,
        data={"evaluation_id": eval_id},
    )

    if response["query_results"] is None:
        return RetrieveEvalResponse(
            status=EvalStatus(response["status"]),
        )

    query_results = []
    for query_result_json in response["query_results"]:
        listing_results = []
        for listing_result_json in query_result_json["listing_results"]:
            listing_results.append(ListingResult(**listing_result_json))

        listing_results = sorted(listing_results, key=lambda x: x.rank)

        max_results = query_result_json["search_request"]["max_results"]
        categories = query_result_json["search_request"]["categories"]
        precision_at_k = query_result_json["metrics"]["precision_at_k"]

        query_results.append(
            QueryResult(
                search_request=SearchRequest(
                    query=query_result_json["search_request"]["query"],
                    max_results=max_results,
                    categories=categories,
                ),
                metrics=Metrics(precision_at_k=precision_at_k),
                listing_results=listing_results,
            )
        )

    return RetrieveEvalResponse(
        status=EvalStatus(response["status"]),
        query_results=query_results,
    )
