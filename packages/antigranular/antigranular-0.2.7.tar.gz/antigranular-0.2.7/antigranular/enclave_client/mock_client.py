import requests
from ..config import config


class MockEnclaveClient:
    """
    Class to test AGClient when the AG Server with Oblv enclave is not available.
    Instead using AG private python server directly(passing custom x_oblv_user_name headers).
    """

    def __init__(
        self,
        ENCLAVE_URL,
        ENCLAVE_PORT,
        pcr_check,
        key,
        pcr0,
        pcr1,
        pcr2,
        auth_type,
        client_id,
        client_secret,
        oauth_audience,
        oauth_url,
        x_oblv_user_name,
        headers={},
    ):
        self.url = ENCLAVE_URL
        self.port = str(ENCLAVE_PORT)
        if x_oblv_user_name:
            headers["x-oblv-user-name"] = x_oblv_user_name
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def update_headers(self, headers):
        self.session.headers.update(headers)

    def get(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "GET", endpoint, data=data, json=json, params=params, headers=headers
        )

    def post(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "POST", endpoint, data=data, json=json, params=params, headers=headers
        )

    def put(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "PUT", endpoint, data=data, json=json, params=params, headers=headers
        )

    def delete(self, endpoint, data=None, json=None, params=None, headers=None):
        return self._make_request(
            "DELETE", endpoint, data=data, json=json, params=params, headers=headers
        )

    def _make_request(
        self, method, endpoint, data=None, json=None, params=None, headers=None
    ):
        if headers:
            with self.session as s:
                s.headers.update(headers)
                response = s.request(method, endpoint, json=json, params=params)
                s.headers.update(self.session.headers)
        else:
            response = self.session.request(
                method, endpoint, data=data, json=json, params=params
            )
        return response


def get_mock_client(ag_client_id, ag_client_secret, x_oblv_user_name):
    """
    Connect to AG Enclave Server and initialize the Oblv client, AG Enclave Server URL and port from config.
    """
    return MockEnclaveClient(
        config.AG_ENCLAVE_URL,
        config.AG_ENCLAVE_PORT,
        True,
        "3030",
        pcr0=config.AG_PCRS["PCR0"],
        pcr1=config.AG_PCRS["PCR1"],
        pcr2=config.AG_PCRS["PCR2"],
        auth_type="oauth",
        client_id=ag_client_id,
        client_secret=ag_client_secret,
        oauth_audience=config.AG_AUDIENCE_URL,
        oauth_url=config.AG_OAUTH_URL,
        x_oblv_user_name=x_oblv_user_name,
    )
