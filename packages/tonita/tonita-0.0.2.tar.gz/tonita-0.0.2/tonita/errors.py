class TonitaError(Exception):
    """Raise when a response does not return a 200 status code."""

    def __init__(self, message):
        super().__init__(message)


class TonitaBadRequestError(TonitaError):
    """Raise for HTTP error code 400 (Bad Request)."""

    pass


class TonitaUnauthorizedError(TonitaError):
    """Raise for HTTP error code 401 (Unauthorized)."""

    pass


class TonitaInternalServerError(TonitaError):
    """Raise for HTTP error code 500 (Internal Server Error)."""

    pass


class TonitaNotImplementedError(TonitaError):
    """Raise for HTTP error code 501 (Not Implemented) or if unimplemented."""

    pass
