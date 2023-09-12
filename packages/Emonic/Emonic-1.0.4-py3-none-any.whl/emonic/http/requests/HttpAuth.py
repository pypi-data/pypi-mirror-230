import base64

class HttpAuth:
    def __init__(self, auth_type='basic', auth_data=None):
        """
        Initialize the HttpAuth object.

        Args:
            auth_type (str): The authentication type ('basic', 'bearer', 'digest', 'oauth2', 'custom').
            auth_data (dict): Authentication data (credentials or tokens).

        Usage:
            auth = HttpAuth()
        """
        self.auth_type = auth_type
        self.auth_data = auth_data or {}

    def basic(self, username, password):
        """
        Set authentication data for Basic authentication.

        Args:
            username (str): The username.
            password (str): The password.

        Returns:
            HttpAuth: The HttpAuth object.

        Usage:
            auth = HttpAuth().basic('user', 'password')
        """
        self.auth_type = 'basic'
        self.auth_data = {'username': username, 'password': password}
        return self

    def bearer(self, token):
        """
        Set authentication data for Bearer authentication.

        Args:
            token (str): The bearer token.

        Returns:
            HttpAuth: The HttpAuth object.

        Usage:
            auth = HttpAuth().bearer('bearer_token')
        """
        self.auth_type = 'bearer'
        self.auth_data = {'token': token}
        return self

    def digest(self, username, realm, nonce, uri, response, algorithm='MD5'):
        """
        Set authentication data for Digest authentication.

        Args:
            username (str): The username.
            realm (str): The realm.
            nonce (str): The nonce.
            uri (str): The URI.
            response (str): The response.
            algorithm (str): The algorithm (default is 'MD5').

        Returns:
            HttpAuth: The HttpAuth object.

        Usage:
            auth = HttpAuth().digest('user', 'realm', 'nonce', 'uri', 'response', 'MD5')
        """
        self.auth_type = 'digest'
        self.auth_data = {
            'username': username,
            'realm': realm,
            'nonce': nonce,
            'uri': uri,
            'response': response,
            'algorithm': algorithm
        }
        return self

    def oauth2(self, token_type, access_token):
        """
        Set authentication data for OAuth2 authentication.

        Args:
            token_type (str): The token type.
            access_token (str): The access token.

        Returns:
            HttpAuth: The HttpAuth object.

        Usage:
            auth = HttpAuth().oauth2('Bearer', 'access_token')
        """
        self.auth_type = 'oauth2'
        self.auth_data = {'token_type': token_type, 'access_token': access_token}
        return self

    def custom(self, auth_type, auth_data):
        """
        Set custom authentication data.

        Args:
            auth_type (str): The custom authentication type.
            auth_data (dict): Custom authentication data.

        Returns:
            HttpAuth: The HttpAuth object.

        Usage:
            auth = HttpAuth().custom('custom_type', {'key': 'value'})
        """
        self.auth_type = auth_type
        self.auth_data = auth_data
        return self

    def set_param(self, key, value):
        """
        Set a parameter in the authentication data.

        Args:
            key (str): The parameter key.
            value (str): The parameter value.

        Returns:
            HttpAuth: The HttpAuth object.

        Usage:
            auth = HttpAuth().set_param('key', 'value')
        """
        self.auth_data[key] = value
        return self

    def get_param(self, key):
        """
        Get a parameter from the authentication data.

        Args:
            key (str): The parameter key.

        Returns:
            str: The parameter value or None if not found.

        Usage:
            value = auth.get_param('key')
        """
        return self.auth_data.get(key)

    def clear_params(self):
        """
        Clear all parameters in the authentication data.

        Returns:
            HttpAuth: The HttpAuth object.

        Usage:
            auth = auth.clear_params()
        """
        self.auth_data = {}
        return self

    def get_auth_header(self):
        """
        Get the authentication header based on the authentication type.

        Returns:
            dict: The authentication header.

        Raises:
            ValueError: If the authentication type is unsupported.

        Usage:
            header = auth.get_auth_header()
        """
        if self.auth_type == 'basic':
            user_pass = f"{self.auth_data['username']}:{self.auth_data['password']}"
            basic_auth = base64.b64encode(user_pass.encode()).decode()
            return {"Authorization": f"Basic {basic_auth}"}
        elif self.auth_type == 'bearer':
            return {"Authorization": f"Bearer {self.auth_data['token']}"}
        elif self.auth_type == 'digest':
            # Implement Digest authentication header construction here
            pass
        elif self.auth_type == 'oauth2':
            return {"Authorization": f"{self.auth_data['token_type']} {self.auth_data['access_token']}"}
        elif self.auth_type == 'custom':
            # Implement custom authentication header construction here
            pass
        else:
            raise ValueError("Unsupported authentication type")

    def __str__(self):
        return f"HttpAuth({self.auth_type}, {self.auth_data})"
    
    def set_auth_type(self, auth_type):
        self.auth_type = auth_type
        return self

    def get_auth_type(self):
        return self.auth_type

    def set_username(self, username):
        self.auth_data['username'] = username
        return self

    def get_username(self):
        return self.auth_data.get('username', None)

    def set_password(self, password):
        self.auth_data['password'] = password
        return self

    def get_password(self):
        return self.auth_data.get('password', None)

    def set_token(self, token):
        self.auth_data['token'] = token
        return self

    def get_token(self):
        return self.auth_data.get('token', None)

    def set_realm(self, realm):
        self.auth_data['realm'] = realm
        return self

    def get_realm(self):
        return self.auth_data.get('realm', None)

    def set_nonce(self, nonce):
        self.auth_data['nonce'] = nonce
        return self

    def get_nonce(self):
        return self.auth_data.get('nonce', None)

    def set_uri(self, uri):
        self.auth_data['uri'] = uri
        return self

    def get_uri(self):
        return self.auth_data.get('uri', None)

    def set_response(self, response):
        self.auth_data['response'] = response
        return self

    def get_response(self):
        return self.auth_data.get('response', None)

    def set_algorithm(self, algorithm):
        self.auth_data['algorithm'] = algorithm
        return self

    def get_algorithm(self):
        return self.auth_data.get('algorithm', None)

    def set_token_type(self, token_type):
        self.auth_data['token_type'] = token_type
        return self

    def get_token_type(self):
        return self.auth_data.get('token_type', None)

    def set_access_token(self, access_token):
        self.auth_data['access_token'] = access_token
        return self

    def get_access_token(self):
        return self.auth_data.get('access_token', None)