"""Functions for corpus-related operations.

    Typical example usage:

    import tonita

    # We first add a corpus.

    # Option 1: Set an API key to use for subsequent calls. This will be
    # overridden if a key is specified in the call itself. If the environment
    # variable `TONITA_API_KEY` is set, `tonita.api_key` will already be equal
    # to that value.
    tonita.api_key = "my-api-key"
    tonita.corpora.add(corpus_id="my-corpus-id")

    # Option 2: Specify the API key in the API call. This will override the
    # value of `tonita.api_key`.
    tonita.corpora.add(
        corpus_id="another-corpus-id",
        api_key="another-api-key"
    )

    # List available corpora. Since an API key was not specified in the call,
    # this call will use the value of `tonita.api_key`.
    tonita.corpora.list()

    # Check that a corpus exists.
    tonita.corpora.exists(corpus_id="my-corpus-id")

    # Delete a corpus.
    tonita.corpora.delete(corpus_id="my-corpus-id")
"""

from typing import Optional

from tonita.api.helpers import _get_module_var_value, _request
from tonita.constants import (
    CORPORA_PATH_ROOT_NAME,
    CORPUS_ID_NAME,
    HTTP_METHOD_POST,
)
from tonita.datatypes.corpora import (
    AddCorpusResponse,
    CorpusExistsResponse,
    DeleteCorpusResponse,
    ListCorporaResponse,
    RecoverCorpusResponse,
    State,
)

# Defaults to "corpora" unless set manually by the user in the environment.
CORPORA_PATH_ROOT = _get_module_var_value(CORPORA_PATH_ROOT_NAME)


def add(corpus_id: str, api_key: Optional[str] = None) -> AddCorpusResponse:
    """Add a corpus.

    Args:
        corpus_id (str):
            The ID of the corpus to add.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        AddCorpusResponse:
            See docstring for `datatypes.corpora.AddCorpusResponse`.

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
        url_path=f"{CORPORA_PATH_ROOT}/add",
        api_key=api_key,
        data={CORPUS_ID_NAME: corpus_id},
    )

    return AddCorpusResponse(**response)


def list(api_key: Optional[str] = None) -> ListCorporaResponse:
    """List all available corpora.

    Args:
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        ListCorporaResponse:
            See docstring for datatypes.corpora.ListCorporaResponse.

    Raises:
        TonitaInternalServerError:
            A server-side error occurred.
        TonitaUnauthorizedError:
            The API key is missing or invalid.
    """

    response = _request(
        method=HTTP_METHOD_POST,
        url_path=f"{CORPORA_PATH_ROOT}/list",
        api_key=api_key,
        data="{}",
    )

    response = ListCorporaResponse(**response)

    for corpus_id, state in response.results.items():
        response.results[corpus_id] = State(state)

    return response


def exists(
    corpus_id: str, api_key: Optional[str] = None
) -> CorpusExistsResponse:
    """Check existence of a corpus.

    Args:
        corpus_id (str):
            The ID of the corpus to check for existence.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        CorpusExistsResponse:
            See docstring for `datatypes.corpora.CorpusExistsResponse`.

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
        url_path=f"{CORPORA_PATH_ROOT}/exists",
        api_key=api_key,
        data={CORPUS_ID_NAME: corpus_id},
    )

    response = CorpusExistsResponse(**response)

    if response.state is not None:
        response.state = State(response.state)

    return response


def delete(
    corpus_id: str, api_key: Optional[str] = None
) -> DeleteCorpusResponse:
    """Delete a corpus.

    This method technically only "marks" a corpus to be deleted after some
    period of time. Until then, the user can still recover the corpus and
    restore access to that corpus' listings by calling `recover()`.

    However, after a sufficiently long time has elapsed (indicated by the
    `seconds_to_expiration` field returned by `exists()`), a corpus that has
    been deleted cannot be recovered.

    Args:
        corpus_id (str):
            The ID of the corpus to delete.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        DeleteCorpusResponse:
            See docstring for `datatypes.corpora.DeleteCorpusResponse`.

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
        url_path=f"{CORPORA_PATH_ROOT}/delete",
        api_key=api_key,
        data={CORPUS_ID_NAME: corpus_id},
    )

    return DeleteCorpusResponse(**response)


def recover(
    corpus_id: str, api_key: Optional[str] = None
) -> RecoverCorpusResponse:
    """Recover a corpus that was previously marked to be deleted.

    Args:
        corpus_id (str):
            The ID of the corpus to recover.
        api_key (Optional[str]):
            An API key. If this argument is `None`, then the value of
            `tonita.api_key` will be used.

    Returns:
        RecoverCorpusResponse:
            See docstring for `datatypes.corpora.RecoverCorpusResponse`.

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
        url_path=f"{CORPORA_PATH_ROOT}/recover",
        api_key=api_key,
        data={CORPUS_ID_NAME: corpus_id},
    )

    return RecoverCorpusResponse(**response)
