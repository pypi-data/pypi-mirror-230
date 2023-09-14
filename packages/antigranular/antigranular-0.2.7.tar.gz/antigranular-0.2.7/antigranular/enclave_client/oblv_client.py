import oblv_client
from ..config import config
import uuid


def get_oblv_client(ag_client_id, ag_client_secret):
    """
    Connect to AG Enclave Server and initialize the Oblv client, AG Enclave Server URL and port from config.
    """
    enclave_client = oblv_client.Enclave(
        config.AG_ENCLAVE_URL,
        config.AG_ENCLAVE_PORT,
        True,
        str(uuid.uuid4()),
        pcr0=config.AG_PCRS["PCR0"],
        pcr1=config.AG_PCRS["PCR1"],
        pcr2=config.AG_PCRS["PCR2"],
        auth_type="oauth",  # hardcoding OAuth for AG Client
        client_id=ag_client_id,
        client_secret=ag_client_secret,
        oauth_audience=config.AG_AUDIENCE_URL,
        oauth_url=config.AG_OAUTH_URL,
    )

    enclave_client.attest()
    return enclave_client
