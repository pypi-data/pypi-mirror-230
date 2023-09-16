import unittest
from unittest.mock import patch
from keycloak import KeycloakOpenID
from kdp_connector.configuration.keycloak_authentication import KeycloakAuthentication

class TestKeycloak(unittest.TestCase):

    def setup(self):
        self.client_id = 'client_id-01'
        self.client_secret = 'ec78c6bb-8339-4bed-9b1b-e973d27107dc'
        self.username = 'aUser'
        self.password = 'mypassword123'
        self.realm = 'testRealm'
        self.host = 'localhost'

        self.workspace_id = 'testws'

        self.keycloak = KeycloakAuthentication()
        self.keycloak.set_configuration(self.realm, self.client_id, self.client_secret, self.username, self.password, self.host)

    def test_keycloak_configuration(self):
        self.setup()
        assert self.keycloak.password is not None
        assert self.keycloak.keycloak_openid.client_id == self.client_id

    def test_get_koverse_authentication_details(self):
        self.setup()
        with patch.object(KeycloakOpenID, 'token', return_value={'access_token': '12345'}) as mock_auth_request:
            self.keycloak.get_keycloak_token()
        mock_auth_request.assert_called_once()


if __name__ == '__main__':
    unittest.main()
