from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from tonita.datatypes.search import SearchRequest

# ******************************** Submit *************************************


@dataclass
class SubmitEvalRequest:
    """Request for a query evaluation."""

    # The search requests whose results to evaluate.
    search_requests: List[SearchRequest]

    # An optional list of email addresses to which notifications should be sent
    # about the status of the evaluation.
    email_addresses: List[str] = field(default_factory=lambda: list())


@dataclass
class SubmitEvalResponse:
    """Response to a query evaluation submission.

    This dataclass contains the evaluation ID, which can be used to check the
    status of an evaluation and retrieve its results.
    """

    # The ID of this evaluation.
    eval_id: str


# ******************************* Retrieve ************************************


class EvalStatus(Enum):
    """The status of an evaluation.

    Values:
        SUBMITTED:
            The evaluation was successfully submitted.
        IN_PROGRESS:
            The evaluation is currently being processed.
        COMPLETED:
            The evaluation has been completed.
        FAILED:
            The evaluation failed.
        INVALID:
            The evaluation is invalid (i.e., does not exist).
    """

    SUBMITTED = 1
    IN_PROGRESS = 2
    COMPLETED = 3
    FAILED = 4
    INVALID = 5


@dataclass
class Metrics:
    """Information retrieval metrics for an evaluated query."""

    # Precision@k, where each key is an integer for `k` and each value is the
    # precision value.
    precision_at_k: Dict[int, float]


@dataclass
class ListingResult:
    """Result for a single listing within a query."""

    # The ID of the listing.
    listing_id: str

    # The rank of this listing in the search results given the query.
    rank: int

    # The score of this listing in the search results given the query.
    score: float

    # The evaluation rating of this listing given the query: 1 if relevant and
    # 0 if irrelevant.
    rating: int


@dataclass
class QueryResult:
    """The result for a single query."""

    # The search request associated with this query.
    search_request: SearchRequest

    # Evaluation metrics for this query.
    metrics: Metrics

    # The results of the search for this particular query. Each element
    # corresponds to a listing returned in the search results, and elements are
    # sorted in decreasing order of its score.
    listing_results: List[ListingResult]


@dataclass
class RetrieveEvalResponse:
    """Response for an evaluation retrieval.

    This dataclass will return the status of the evaluation and the evaluation
    results if they are available.
    """

    # The status of the evaluation.
    status: EvalStatus

    # The evaluation results; one element for each query submitted. This will
    # be `None` if the status is `IN_PROGRESS` or `FAILED`, and will contain
    # results only for a subset of queries submitted if `NEAR_COMPLETED`.
    query_results: Optional[List[QueryResult]] = None
