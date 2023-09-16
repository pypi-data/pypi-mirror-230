from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SearchRequest:
    """A request to retrieve listings relevant to a given query."""

    # The natural language query for which relevant listings are retrieved.
    query: Optional[str]

    # An intent is a short phrase that represents one atomic portion of what
    # a user wants.  For each intent, the caller may additionally provide
    # a score that tells us how important this intent is to the user.
    # Each dict must have the key "text". It may also have the key "score".
    # Example:
    # [
    #     {"text": "romantic comedy", "score": 8.0},
    #     {"text": "great acting", "score": 4.0},
    #     {"text": "funny courtroom scenes", "score": 1.0}
    # ]
    # Here, the user primarily wants a romantic comedy, places a significant
    # (relative) value on great acting, and mentions "funny courtroom scenes"
    # as a nice-to-have.
    intents: Optional[List[Dict[str, Any]]] = None

    # The maximum number of results to return. For evaluation, this field must
    # be `None`. For search, if this is set to `None`, a default value of 10
    # will be used.
    max_results: int = 10

    # If given, search is restricted to listings within these categories.
    # If omitted, search is restricted to listings without any category attached.
    categories: Optional[List[str]] = None

    # If facet restrictions are provided, search results will give greater
    # preference to listings that satisfy a greater number of restrictions.
    #
    # Each restriction is expressed as a dict with the following keys:
    #   1. "name": Required. The name of the facet. For example, "price".
    #   2. "type": Required. The type of the facet across listings that the
    #       restriction is based on. This will determine how the facet value is
    #       handled (i.e., what operations are valid for it). For example, each
    #       listing may have a "price" facet that is numeric, or a "genre"
    #       facet that is a string.
    #       Valid values for this field are "STRING", "NUMERIC", and "BOOLEAN".
    #   3. "operation": Required. The operation for the restriction. For
    #       example, if the value of some numeric facet must be greater than or
    #       equal to 9, the operation would be "GREATER_THAN_EQUAL".
    #       Valid values are "EQUAL", "LESS_THAN", "LESS_THAN_EQUAL",
    #       "GREATER_THAN", "GREATER_THAN_EQUAL", and "ONE_OF".
    #   4. "value": Required. The value used for the restriction. Note that
    #       this is not necessarily the same as the facet value. For example, a
    #       restriction that movies must be one of three genres would have
    #       "value" be `["comedy", "drama", "thriller"]`, but the facet value
    #       for a movie that satisfies the restriction would just be "genre x".
    #       On the other hand, a restriction that the facet for "director" be
    #       "Jane Doe" would set the "value" field of the restriction to "Jane
    #       Doe".
    #   5. "weight": Optional. An importance weight for the facet. This weight
    #       does not need to be normalized across facet restrictions. Weights
    #       must be provided either for all of the restrictions or for none of
    #       them. If no weights are provided, equal weights across restrictions
    #       will be assumed. Facets with zero or negative weight will be
    #       ignored.
    #
    # Consider the following example set of facet restrictions for books:
    #
    # [
    #     {
    #         "name": "pages",
    #         "type": "NUMERIC",
    #         "operation": "LESS_THAN_EQUAL",
    #         "value": 500,
    #         "weight": 3.14,
    #     },
    #     {
    #         "name": "language",
    #         "type": "STRING",
    #         "operation": "ONE_OF",
    #         "value": ["english", "portuguese", "korean"],
    #         "weight": 2.72,
    #     },
    # ]
    #
    # Here, we have two restrictions: one that the number of pages of the book
    # be less than 500, and one that the language of the book must be either
    # English, Portuguese, or Korean. The importance weights denote that the
    # restriction on the number of pages is slightly more important than the
    # restriction on language.
    facet_restrictions: Optional[List[Dict[str, Any]]] = None


@dataclass
class Snippet:
    """Explains why a listing was considered relevant to a query."""

    # We simply return a single string that describes the basis
    # for why a response item was returned. The caller may choose to use this,
    # e.g. for displaying as a highlighted snippet under the title of the
    # result.
    display_string: str


@dataclass
class SearchResponseItem:
    """A single search result."""

    # The ID of a listing considered relevant to the query.
    listing_id: str

    # A higher score denotes a better match to the query.
    score: float

    # The set of categories this listing belongs to.
    categories: List[str]

    # Explains why this listing was considered a relevant match for the query.
    snippets: List[Snippet]


@dataclass
class SearchResponse:
    """Response to a search request."""

    # A list of search results.
    items: List[SearchResponseItem]

    # JSON-stringified object that contains debug info.
    debug_info_json: Optional[str] = None
