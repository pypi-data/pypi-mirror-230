"""A library for interacting with ActiGraph's API."""


class ActiGraphClient:
    """Base classe for ActiGraph API clients.

    Parameters
    ----------
    api_access_key
        API access key
    api_secret_key
        API secret key
    """

    def __init__(self, api_access_key: str, api_secret_key: str):
        """Initialize client."""
        self.api_access_key = api_access_key
        self.api_secret_key = api_secret_key
