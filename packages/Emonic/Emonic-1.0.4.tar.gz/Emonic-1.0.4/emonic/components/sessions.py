import os
import base64
from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime, timedelta
import hashlib
import hmac

class SessionManager:
    def __init__(self, secret_key, session_lifetime=3600, cookie_name='session_id', cookie_path='/', secure=False, http_only=True):
        """
        Initialize the SessionManager.

        Args:
            secret_key (bytes): A secret key for encoding and decoding session data.
            session_lifetime (int, optional): The session lifetime in seconds (default is 3600 seconds).
            cookie_name (str, optional): The name of the session cookie (default is 'session_id').
            cookie_path (str, optional): The path for which the session cookie is valid (default is '/').
            secure (bool, optional): Whether the session cookie should only be sent over HTTPS (default is False).
            http_only (bool, optional): Whether the session cookie should be accessible only via HTTP (default is True).
        """
        self.secret_key = secret_key
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.cipher_suite = Fernet(base64.urlsafe_b64encode(secret_key))
        self.session_lifetime = timedelta(seconds=session_lifetime)
        self.cookie_name = cookie_name
        self.cookie_path = cookie_path
        self.secure = secure
        self.http_only = http_only
        self.session_data = {}

    def encode_data(self, data):
        """
        Encode session data.

        Args:
            data (dict): The session data to encode.

        Returns:
            str: The encoded session data.

        Usage:
            encoded_data = session_manager.encode_data({'key': 'value'})
        """
        serialized_data = self.serializer.dumps(data)
        encrypted_data = self.cipher_suite.encrypt(serialized_data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    def decode_data(self, data):
        """
        Decode encoded session data.

        Args:
            data (str): The encoded session data.

        Returns:
            dict: The decoded session data.

        Usage:
            decoded_data = session_manager.decode_data(encoded_data)
        """
        encrypted_data = base64.urlsafe_b64decode(data.encode('utf-8'))
        decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode('utf-8')
        return self.serializer.loads(decrypted_data)

    def generate_expiration(self):
        """
        Generate a session expiration time.

        Returns:
            datetime: The session expiration time.

        Usage:
            expiration = session_manager.generate_expiration()
        """
        return datetime.now() + self.session_lifetime

    def save_session(self, session_data, **kwargs):
        """
        Save session data.

        Args:
            session_data (dict): The session data to save.
            **kwargs: Additional data to include in the session.

        Returns:
            dict: The session data with session ID, expiration, and additional data.

        Usage:
            session_data = session_manager.save_session({'user_id': 123}, username='example')
        """
        session_id = self.encode_data(session_data)
        expiration = self.generate_expiration()
        return {'session_id': session_id, 'expiration': expiration, **kwargs}

    def load_session(self, session_id):
        """
        Load session data.

        Args:
            session_id (str): The session ID.

        Returns:
            dict: The loaded session data or an empty dictionary if the session is not valid.

        Usage:
            session_data = session_manager.load_session('encoded_session_id')
        """
        try:
            session_data = self.decode_data(session_id)
        except Exception:
            session_data = {}
        return session_data

    def is_session_expired(self, expiration):
        """
        Check if a session has expired.

        Args:
            expiration (datetime): The session expiration time.

        Returns:
            bool: True if the session has expired, False otherwise.

        Usage:
            expired = session_manager.is_session_expired(session_expiration)
        """
        return datetime.now() > expiration

    def validate_session(self, session_id):
        """
        Validate a session.

        Args:
            session_id (str): The session ID.

        Returns:
            tuple: A tuple containing a boolean indicating whether the session is valid and the session data (if valid).

        Usage:
            valid, session_data = session_manager.validate_session('encoded_session_id')
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return False, {}
        
        expiration = session_data.get('expiration')
        if expiration and not self.is_session_expired(expiration):
            return True, session_data
        else:
            return False, {}

    def get_cookie_name(self):
        """
        Get the name of the session cookie.

        Returns:
            str: The name of the session cookie.

        Usage:
            cookie_name = session_manager.get_cookie_name()
        """
        return self.cookie_name

    def get_cookie_options(self):
        """
        Get session cookie options.

        Returns:
            dict: Session cookie options including path, secure, and httponly.

        Usage:
            cookie_options = session_manager.get_cookie_options()
        """
        options = {
            'path': self.cookie_path,
            'secure': self.secure,
            'httponly': self.http_only,
        }
        return options

    def generate_signature(self, data):
        """
        Generate a signature for session data.

        Args:
            data (str): The data to sign.

        Returns:
            str: The generated signature.

        Usage:
            signature = session_manager.generate_signature('data_to_sign')
        """
        signature = hmac.new(self.secret_key, data.encode('utf-8'), hashlib.sha256)
        return signature.hexdigest()

    def validate_signature(self, data, signature):
        """
        Validate a signature for session data.

        Args:
            data (str): The data to validate.
            signature (str): The signature to validate against.

        Returns:
            bool: True if the signature is valid, False otherwise.

        Usage:
            valid = session_manager.validate_signature('data_to_validate', 'expected_signature')
        """
        expected_signature = self.generate_signature(data)
        return hmac.compare_digest(expected_signature, signature)
    
    def set_session_lifetime(self, session_lifetime):
        """
        Set the session lifetime.

        Args:
            session_lifetime (int): The session lifetime in seconds.

        Usage:
            session_manager.set_session_lifetime(3600)
        """
        self.session_lifetime = timedelta(seconds=session_lifetime)

    def renew_session(self, session_id):
        """
        Renew an existing session.

        Args:
            session_id (str): The session ID to renew.

        Returns:
            dict: The renewed session data.

        Usage:
            renewed_session_data = session_manager.renew_session('encoded_session_id')
        """
        session_data = self.load_session(session_id)
        if session_data:
            expiration = self.generate_expiration()
            return self.save_session(session_data, expiration=expiration)

    def touch(self, session_id):
        """
        Update the expiration time of an existing session without modifying its content.

        Args:
            session_id (str): The session ID to update.

        Returns:
            dict: The updated session data.

        Usage:
            updated_session_data = session_manager.touch('encoded_session_id')
        """
        session_data = self.load_session(session_id)
        if session_data:
            return self.save_session(session_data)

    def pop(self, key, default=None):
        """
        Remove a key from the session and return its value.

        Args:
            key (str): The key to remove from the session.
            default: The default value to return if the key is not found.

        Returns:
            Any: The value associated with the key or the default value.

        Usage:
            value = session_manager.pop('key', default_value)
        """
        return self.session_data.pop(key, default)

    def clear(self):
        """
        Clear all data from the session.

        Usage:
            session_manager.clear()
        """
        self.session_data.clear()

    def set(self, key, value):
        """
        Set a value in the session.

        Args:
            key (str): The key to set.
            value: The value to associate with the key.

        Usage:
            session_manager.set('key', 'value')
        """
        self.session_data[key] = value

    def get(self, key, default=None):
        """
        Get a value from the session.

        Args:
            key (str): The key to get.
            default: The default value to return if the key is not found.

        Returns:
            Any: The value associated with the key or the default value.

        Usage:
            value = session_manager.get('key', default_value)
        """
        return self.session_data.get(key, default)

    def update(self, data):
        """
        Update session data with a dictionary.

        Args:
            data (dict): The dictionary containing data to update the session with.

        Usage:
            session_manager.update({'key1': 'value1', 'key2': 'value2'})
        """
        self.session_data.update(data)

# Create a global instance of the session manager
secret_key = os.urandom(32)
session_manager = SessionManager(secret_key)
