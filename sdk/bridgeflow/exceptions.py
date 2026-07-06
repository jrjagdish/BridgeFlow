"""Exceptions raised by the BridgeFlow SDK."""


class BridgeFlowError(Exception):
    """Base class for all BridgeFlow SDK errors."""


class AuthenticationError(BridgeFlowError):
    """Raised when no API key is configured, or the server rejects it (401)."""


class APIError(BridgeFlowError):
    """
    Raised when the BridgeFlow API returns a non-2xx response
    (other than an auth failure, which raises AuthenticationError).
    """

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"BridgeFlow API error {status_code}: {detail}")


class ConnectionError(BridgeFlowError):
    """Raised when the BridgeFlow server can't be reached at all."""
