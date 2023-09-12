import base64
import json
import datetime
import uuid
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hmac as hmac_primitives
import secrets
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class JwT:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self.tokens = {}  

    def encode(self, payload, secret_key=None, private_key=None, algorithm='HS256', exp=None, nbf=None, aud=None, iss=None, custom_claims=None):
        """
        Encode a JSON Web Token (JWT).

        Args:
            payload (dict): The payload data to be encoded.
            secret_key (str, optional): The secret key for HMAC algorithms.
            private_key (str, optional): The private key for RSA algorithms.
            algorithm (str, optional): The algorithm to use for encoding (e.g., 'HS256', 'RS256').
            exp (int, optional): The expiration time in seconds.
            nbf (int, optional): The "not before" time in seconds.
            aud (str, optional): The audience claim.
            iss (str, optional): The issuer claim.
            custom_claims (dict, optional): Additional custom claims.

        Returns:
            str: The encoded JWT token.

        Usage:
            jwt_token = jwt.encode(
                payload={'sub': '123', 'name': 'John Doe'},
                secret_key='my_secret_key',
                algorithm='HS256',
                exp=3600,
                nbf=0,
                aud='example.com',
                iss='issuer',
                custom_claims={'role': 'admin'}
            )
        """
        header = {'alg': algorithm, 'typ': 'JWT'}
        encoded_header = self._base64_encode(header)
        
        current_time = datetime.datetime.utcnow()
        iat = current_time.timestamp()
        
        if 'iat' not in payload:
            payload['iat'] = iat
        if exp is not None and 'exp' not in payload:
            payload['exp'] = iat + exp
        if nbf:
            payload['nbf'] = iat + nbf
        if aud:
            payload['aud'] = aud
        if iss:
            payload['iss'] = iss
        if custom_claims:
            payload.update(custom_claims)
        
        encoded_payload = self._base64_encode(payload)
        
        if algorithm.startswith('HS'):
            if not secret_key:
                raise ValueError("Secret key is required for HMAC algorithm")
            signature = self._sign_hmac(encoded_header + '.' + encoded_payload, secret_key, algorithm)
        elif algorithm.startswith('RS'):
            if not private_key:
                raise ValueError("Private key is required for RSA algorithm")
            signature = self._sign_rsa(encoded_header + '.' + encoded_payload, private_key, algorithm)
        else:
            raise ValueError("Unsupported algorithm")
        
        jwt_token = f"{encoded_header}.{encoded_payload}.{signature}"
        return jwt_token
    
    def decode(self, jwt_token, secret_key=None, public_key=None, custom_claims=None):
        """
        Decode a JSON Web Token (JWT).

        Args:
            jwt_token (str): The JWT token to decode.
            secret_key (str, optional): The secret key for HMAC algorithms.
            public_key (str, optional): The public key for RSA algorithms.
            custom_claims (dict, optional): Additional custom claims for validation.

        Returns:
            dict: The decoded payload.

        Raises:
            ValueError: If the token is invalid or expired.

        Usage:
            payload = jwt.decode(jwt_token, secret_key='my_secret_key', algorithm='HS256')
        """
        encoded_header, encoded_payload, signature = jwt_token.split('.')
        header = json.loads(self._base64_decode(encoded_header))
        payload = json.loads(self._base64_decode(encoded_payload))
        
        algorithm = header.get('alg')
        if not algorithm:
            raise ValueError("Missing algorithm in header")
        
        if algorithm.startswith('HS'):
            if not secret_key:
                raise ValueError("Secret key is required for HMAC algorithm")
            calculated_signature = self._sign_hmac(encoded_header + '.' + encoded_payload, secret_key, algorithm)
        elif algorithm.startswith('RS'):
            if not public_key:
                raise ValueError("Public key is required for RSA algorithm")
            if not self._verify_rsa(encoded_header + '.' + encoded_payload, signature, public_key, algorithm):
                raise ValueError("Invalid signature")
            calculated_signature = signature
        else:
            raise ValueError("Unsupported algorithm")
        
        if calculated_signature != signature:
            raise ValueError("Invalid signature")
        
        current_time = datetime.datetime.utcnow()

        if 'exp' in payload and current_time.timestamp() > payload['exp']:
            raise ValueError("Token has expired")
        
        if 'nbf' in payload and current_time.timestamp() < payload['nbf']:
            raise ValueError("Token is not yet valid")
        
        # Custom claims validation
        if custom_claims:
            for claim_name, claim_value in custom_claims.items():
                if claim_name not in payload:
                    raise ValueError(f"Custom claim '{claim_name}' is missing")
                if payload[claim_name] != claim_value:
                    raise ValueError(f"Custom claim '{claim_name}' has invalid value")
        
        return payload
    
    def _base64_encode(self, data):
        return base64.urlsafe_b64encode(json.dumps(data).encode('utf-8')).rstrip(b'=').decode('utf-8')
    
    def _base64_decode(self, data):
        padding_length = 4 - (len(data) % 4)
        padded_data = data + '=' * padding_length
        return base64.urlsafe_b64decode(padded_data.encode('utf-8')).decode('utf-8')
    
    def _sign_hmac(self, data, secret_key, algorithm):
        if algorithm == 'HS256':
            hash_algorithm = hashes.SHA256()
        elif algorithm == 'HS384':
            hash_algorithm = hashes.SHA384()
        elif algorithm == 'HS512':
            hash_algorithm = hashes.SHA512()
        else:
            raise ValueError("Unsupported algorithm")
        
        key = secret_key.encode('utf-8')
        h = hmac_primitives.HMAC(key, hash_algorithm)
        h.update(data.encode('utf-8'))
        return base64.urlsafe_b64encode(h.finalize()).decode('utf-8')
    
    def _sign_rsa(self, data, private_key, algorithm):
        from cryptography.hazmat.primitives.asymmetric import utils
        
        if algorithm == 'RS256':
            padding_algorithm = padding.PKCS1v15()
            hash_algorithm = hashes.SHA256()
        elif algorithm == 'RS384':
            padding_algorithm = padding.PKCS1v15()
            hash_algorithm = hashes.SHA384()
        elif algorithm == 'RS512':
            padding_algorithm = padding.PKCS1v15()
            hash_algorithm = hashes.SHA512()
        else:
            raise ValueError("Unsupported algorithm")
        
        key = serialization.load_pem_private_key(private_key.encode('utf-8'), password=None)
        signature = key.sign(data.encode('utf-8'), padding_algorithm, hash_algorithm)
        return base64.urlsafe_b64encode(signature).decode('utf-8')
    
    def _verify_rsa(self, data, signature, public_key, algorithm):
        from cryptography.hazmat.primitives.asymmetric import padding
        
        if algorithm == 'RS256':
            padding_algorithm = padding.PKCS1v15()
            hash_algorithm = hashes.SHA256()
        elif algorithm == 'RS384':
            padding_algorithm = padding.PKCS1v15()
            hash_algorithm = hashes.SHA384()
        elif algorithm == 'RS512':
            padding_algorithm = padding.PKCS1v15()
            hash_algorithm = hashes.SHA512()
        else:
            raise ValueError("Unsupported algorithm")
        
        key = serialization.load_pem_public_key(public_key.encode('utf-8'))
        try:
            key.verify(base64.urlsafe_b64decode(signature), data.encode('utf-8'), padding_algorithm, hash_algorithm)
            return True
        except:
            return False
    
    def generate_private_key(self):
        """
        Generate a private key for use with RSA algorithms.

        Returns:
            str: The PEM-encoded private key.

        Usage:
            private_key = jwt.generate_private_key()
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        return private_key_pem.decode('utf-8')
    
    def generate_public_key(self, private_key):
        """
        Generate a public key from a private key.

        Args:
            private_key (str): The PEM-encoded private key.

        Returns:
            str: The PEM-encoded public key.

        Usage:
            public_key = jwt.generate_public_key(private_key)
        """
        private_key_obj = serialization.load_pem_private_key(private_key.encode('utf-8'), password=None)
        public_key = private_key_obj.public_key()
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_key_pem.decode('utf-8')
    
    def generate_jti(self):
        """
        Generate a unique JWT ID (JTI).

        Returns:
            str: The JTI.

        Usage:
            jti = jwt.generate_jti()
        """
        return str(uuid.uuid4())
    
    def generate_secret_key(self, length=32):
        """
        Generate a secret key for HMAC algorithms.

        Args:
            length (int, optional): The length of the secret key in bytes.

        Returns:
            str: The generated secret key.

        Usage:
            secret_key = jwt.generate_secret_key()
        """
        return secrets.token_hex(length)
    
    def generate_refresh_token(self, secret_key, user_id):
        """
        Generate a refresh token.

        Args:
            secret_key (str): The secret key for HMAC algorithms.
            user_id (str): The user identifier.

        Returns:
            str: The encoded refresh token.

        Usage:
            refresh_token = jwt.generate_refresh_token(secret_key, '123')
        """
        return self.encode({'sub': user_id, 'type': 'refresh'}, secret_key, algorithm='HS256', exp=2592000)  # 30 days

    def generate_access_token(self, secret_key=None, public_key=None, user_id=None, scopes=None, custom_claims=None):
        """
        Generate an access token.

        Args:
            secret_key (str, optional): The secret key for HMAC algorithms.
            public_key (str, optional): The public key for RSA algorithms.
            user_id (str): The user identifier.
            scopes (list, optional): List of scopes for access control.
            custom_claims (dict, optional): Additional custom claims.

        Returns:
            str: The encoded access token.

        Raises:
            ValueError: If user_id is not provided.

        Usage:
            access_token = jwt.generate_access_token(user_id='123', scopes=['read', 'write'])
        """
        if not user_id:
            raise ValueError("User ID is required to generate an access token")
        
        payload = {'sub': user_id}
        
        if scopes:
            payload['scopes'] = scopes
        
        if custom_claims:
            payload.update(custom_claims)
        
        return self.encode(payload, secret_key=secret_key, public_key=public_key, algorithm='HS256')
        
    def extend_expiration(self, jwt_token, new_exp=None):
        """
        Extend the expiration time of a JWT token.

        Args:
            jwt_token (str): The JWT token to extend.
            new_exp (int, optional): The new expiration time in seconds.

        Returns:
            str: The extended JWT token.

        Usage:
            extended_token = jwt.extend_expiration(jwt_token, new_exp=3600)
        """
        payload = self.decode(jwt_token, secret_key=None, public_key=None)
        
        if new_exp is not None:
            payload['exp'] = new_exp
        
        return self.encode(payload, secret_key=None, public_key=None)
    
    def revoke_token(self, jwt_token, blacklist):
        """
        Revoke a JWT token by adding its JTI to a blacklist.

        Args:
            jwt_token (str): The JWT token to revoke.
            blacklist (set): The set to store revoked JTI values.

        Returns:
            bool: True if the token was successfully revoked, False otherwise.

        Usage:
            revoked = jwt.revoke_token(jwt_token, my_blacklist)
        """
        payload = self.decode(jwt_token, secret_key=None, public_key=None)
        
        jti = payload.get('jti')
        if not jti:
            return False
        
        if jti in blacklist:
            return False
        
        blacklist.add(jti)
        return True
    
    def rotate_keys(self):
        """
        Rotate the JWT keys, generating new private and public keys.

        Returns:
            tuple: A tuple containing the new private key, new public key, and updated tokens.

        Usage:
            new_private_key, new_public_key, updated_tokens = jwt.rotate_keys()
        """
        new_private_key = self.generate_private_key()
        new_public_key = self.generate_public_key(new_private_key)

        if self.private_key and self.public_key:
            updated_tokens = self._reencode_tokens(self.private_key, new_private_key, self.public_key, new_public_key)
        else:
            updated_tokens = {}

        self.private_key = new_private_key
        self.public_key = new_public_key

        return new_private_key, new_public_key, updated_tokens

    def _reencode_tokens(self, old_private_key, new_private_key, old_public_key, new_public_key):
        updated_tokens = {}

        for old_token, old_token_payload in self.tokens.items():
            try:
                decoded_payload = self.decode(old_token, secret_key=None, public_key=old_public_key)
            except ValueError:
                continue

            new_token = self.encode(decoded_payload, secret_key=None, public_key=new_public_key)
            updated_tokens[old_token] = new_token

        return updated_tokens
