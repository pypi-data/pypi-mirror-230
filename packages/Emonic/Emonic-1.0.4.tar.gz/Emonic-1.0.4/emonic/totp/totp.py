import hashlib
import hmac
import time
import secrets
import qrcode
import urllib.parse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class Emonictpt:
    def __init__(self, secret=None, algorithm='sha1', digits=6, interval=30, key_rotation=False):
        """
        Initialize the Emonictpt (Time-Based One-Time Password) generator.

        Args:
            secret (bytes): The secret key for generating OTPs.
            algorithm (str): The hash algorithm to use ('sha1' or 'sha256').
            digits (int): The number of OTP digits.
            interval (int): The OTP time interval in seconds.
            key_rotation (bool): Enable key rotation for multiple keys.

        Usage:
            totp = Emonictpt(secret=b'my_secret_key', algorithm='sha256')
        """
        self.algorithm = algorithm
        self.digits = digits
        self.interval = interval
        self.key_rotation = key_rotation
        self.keys = [self.generate_secret()]
        self.rate_limit = {}
        
        if secret:
            self.add_key(secret)

    def add_key(self, secret):
        """
        Add a new secret key for OTP generation.

        Args:
            secret (bytes): The secret key to add.

        Usage:
            totp.add_key(b'new_secret_key')
        """
        self.keys.append(secret.encode())

    @staticmethod
    def generate_secret():
        """
        Generate a new secret key.

        Returns:
            bytes: The generated secret key.

        Usage:
            secret = Emonictpt.generate_secret()
        """
        try:
            salt = secrets.token_bytes(16)
            password = secrets.token_urlsafe(32).encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                iterations=100000,
                salt=salt,
                length=32,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key
        except Exception as e:
            raise Exception("Error generating secret: " + str(e))

    @staticmethod
    def _int_to_bytestring(i, padding=8):
        return i.to_bytes(padding, byteorder='big')

    def _generate_otp_hash(self, value, secret_key):
        try:
            algorithm = hashlib.sha1 if self.algorithm == 'sha1' else hashlib.sha256
            value_bytes = self._int_to_bytestring(value, padding=8)
            hmac_digest = hmac.new(secret_key, value_bytes, algorithm).digest()
            offset = hmac_digest[-1] & 0x0F
            truncated_hash = hmac_digest[offset:offset + 4]
            return int.from_bytes(truncated_hash, byteorder='big') & 0x7FFFFFFF
        except Exception as e:
            raise Exception("Error generating OTP hash: " + str(e))

    def generate_totp(self, timestamp=None):
        """
        Generate a Time-Based One-Time Password (TOTP).

        Args:
            timestamp (int): The timestamp for which to generate the OTP.

        Returns:
            tuple: A tuple containing the generated OTP(s).

        Usage:
            otp1, otp2 = totp.generate_totp()
        """
        try:
            if timestamp is None:
                timestamp = int(time.time()) // self.interval
            self._rate_limit_check()
            otp1 = self._generate_otp_hash(timestamp // self.interval, self.keys[0])
            
            if self.key_rotation and len(self.keys) > 1:
                otp2 = self._generate_otp_hash(timestamp // self.interval, self.keys[1])
                return otp1, otp2
            else:
                return otp1, None
        except Exception as e:
            raise Exception("Error generating TOTP: " + str(e))

    def _rate_limit_check(self):
        try:
            current_time = int(time.time())
            if self.rate_limit.get(self.keys[0], 0) + self.interval > current_time:
                raise Exception("Rate limit exceeded")
            self.rate_limit[self.keys[0]] = current_time
        except Exception as e:
            raise Exception("Error checking rate limit: " + str(e))

    def generate_qr_code(self, provisioning_url):
        """
        Generate a QR code for provisioning a TOTP generator.

        Args:
            provisioning_url (str): The provisioning URL for the OTP generator.

        Usage:
            totp.generate_qr_code('otpauth://totp/MyApp:alice?secret=SECRETKEY&algorithm=sha256')
        """
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(provisioning_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save('qrcode.png')

    def provisioning_uri(self, name, issuer_name=None, initial_counter=None):
        """
        Generate a provisioning URI for configuring an OTP generator.

        Args:
            name (str): The account name.
            issuer_name (str): The issuer name (optional).
            initial_counter (int): The initial counter value (optional).

        Returns:
            str: The provisioning URI.

        Usage:
            uri = totp.provisioning_uri('alice', 'MyApp')
        """
        try:
            secret = urllib.parse.quote(base64.urlsafe_b64encode(self.keys[0]).decode())
            label = urllib.parse.quote(name)
            params = [
                f'secret={secret}',
                f'algorithm={self.algorithm}',
                f'digits={self.digits}',
                f'period={self.interval}'
            ]
            if initial_counter is not None:
                params.append(f'counter={initial_counter}')
            if issuer_name:
                issuer = urllib.parse.quote(issuer_name)
                return f'otpauth://totp/{issuer}:{label}?{"&".join(params)}'
            else:
                return f'otpauth://totp/{label}?{"&".join(params)}'
        except Exception as e:
            raise Exception("Error generating provisioning URI: " + str(e))
