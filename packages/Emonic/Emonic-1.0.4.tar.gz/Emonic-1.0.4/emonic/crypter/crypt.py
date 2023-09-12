import base64
import bcrypt
import hmac
import string
import random
from itsdangerous import URLSafeTimedSerializer
from cryptography.fernet import Fernet

class Bcrypt:
    def __init__(self, app=None):
        self._log_rounds = 12
        self._default_rounds = 12
        self._supported_prefixes = [b'2a', b'2b']

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._log_rounds = app.config.get('BCRYPT_LOG_ROUNDS', self._default_rounds)
        self.secret_key = app.secret_key
        self.serializer = URLSafeTimedSerializer(base64.urlsafe_b64encode(self.secret_key))

    @staticmethod
    def _unicode_to_bytes(unicode_string):
        return unicode_string.encode('utf-8') if isinstance(unicode_string, str) else unicode_string

    def generate_salt(self, prefix=None, rounds=None):
        if prefix is None or prefix.encode('utf-8') not in self._supported_prefixes:
            prefix = self._supported_prefixes[0].decode('utf-8')  # Default to '2a' prefix

        if rounds is None or not isinstance(rounds, int) or rounds < 4 or rounds > 31:
            rounds = self._log_rounds

        rounds = 15 

        return bcrypt.gensalt(prefix=prefix.encode('utf-8'), rounds=rounds)

    def generate_secret_key(self, key_length=32):
        return Fernet.generate_key()

    def generate_password(self, length=12):
        charset = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(charset) for _ in range(length))

    def generate_password_hash(self, password):
        if not password:
            raise ValueError('Password must be non-empty.')

        password = self._unicode_to_bytes(password)
        salt = self.generate_salt()

        return bcrypt.hashpw(password, salt)

    def check_password_hash(self, pw_hash, password):
        pw_hash = self._unicode_to_bytes(pw_hash)
        password = self._unicode_to_bytes(password)

        return hmac.compare_digest(bcrypt.hashpw(password, pw_hash), pw_hash)