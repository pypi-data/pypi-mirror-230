"""
Configuration file for the AG Client.
"""

AG_EXEC_TIMEOUT = 600  # In seconds

# OAuth Server address to use for authentication
AG_OAUTH_URL = "https://auth.antigranular.com/oauth/token"

# AG Audience URL as set on OAuth Server
AG_AUDIENCE_URL = "https://www.antigranular.com"

# Deployed AG Enclave Server URL for competitions, datasets
AG_ENCLAVE_URL = "https://api.antigranular.com"

# Deployed AG Enclave Server Port - 443 for HTTPS.
AG_ENCLAVE_PORT = 443

AG_SRV_INFO_URL = "https://portal.antigranular.com/server_info"

AG_PCRS = {
    "PCR0": "827d1e6374194549061272703b34aa2618d50e856f48541a0bba1a92bf60ba86f4de141b4a5cc448b089c44a4d5fa825",
    "PCR1": "bcdf05fefccaa8e55bf2c8d6dee9e79bbff31e34bf28a99aa19e6b29c37ee80b214a414b7607236edf26fcb78654e63f",
    "PCR2": "b2ff57dcc660eb5ab6de9de6c830d2b94c6de592288ee1602477b922797915c81cf151678947207cf0d1fd05be57490b",
}
