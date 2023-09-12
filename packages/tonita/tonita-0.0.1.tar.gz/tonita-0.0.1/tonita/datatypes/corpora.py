from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

# ********************************* AddCorpus *********************************


@dataclass
class AddCorpusResponse:
    """Response to a request to add a corpus."""

    # The ID of the corpus to add.
    corpus_id: str


# *********************************** State ***********************************


class State(str, Enum):
    """Denotes the possible states of a corpus."""

    INACTIVE = "INACTIVE"
    ACTIVE = "ACTIVE"


# ******************************** ListCorpora ********************************


@dataclass
class ListCorporaResponse:
    """Response to a request to enumerate all corpora."""

    # Dict mapping from each corpus ID to its state.
    results: Dict[str, State]


# ******************************** CorpusExists *******************************


@dataclass
class CorpusExistsResponse:
    """Response to a request to check if a corpus exists."""

    # The name of the corpus ID in the request.
    corpus_id: str

    # `True` if this corpus exists. This is `False` if the corpus does not
    # exist.
    exists: bool

    # The state of the corpus. This will be `None` if the corpus does not
    # exist.
    state: Optional[State] = None

    # If inactive, the amount of time (in seconds) the corpus has left until it
    # can no longer be recovered. This will be `None` if the corpus does not
    # exist.
    seconds_to_expiration: Optional[float] = None


# ******************************** DeleteCorpus *******************************


@dataclass
class DeleteCorpusResponse:
    """Response to a request to delete a corpus."""

    # The name of the corpus ID in the request.
    corpus_id: str


# ******************************* RecoverCorpus *******************************


@dataclass
class RecoverCorpusResponse:
    """Response to a request to recover a corpus marked to be deleted."""

    # The name of the corpus ID in the request.
    corpus_id: str
