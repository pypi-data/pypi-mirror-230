from mcloud.generated.client import MarimoV1Client
from mcloud.constants import API_URL
from mcloud.auth import get_access_token

def create_marimo_client() -> MarimoV1Client:
    """
    Creates a MarimoV1Client with the default API_URL and access token.
    """
    return MarimoV1Client(environment=API_URL, token=get_access_token())
