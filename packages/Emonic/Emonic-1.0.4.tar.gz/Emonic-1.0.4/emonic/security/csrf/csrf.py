import os
import secrets
import time
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import Forbidden
from itsdangerous import URLSafeSerializer
from functools import wraps

class CSRF:
    def __init__(self, app):
        """
        Initialize the CSRF protection.

        Args:
            app: The WSGI application.

        Usage:
            csrf = CSRF(app)
        """
        self.app = app
        self.csrf_secret_key = os.urandom(32)
        self.cookie_secret_key = os.urandom(32)
        self.token_name = 'csrf_token'
        self.csrf_serializer = URLSafeSerializer(self.csrf_secret_key)
        self.cookie_serializer = URLSafeSerializer(self.cookie_secret_key)
        self.rate_limit_period = 60  # 1 minute
        self.rate_limit_max_requests = 5
        self.rate_limit_storage = {}

    def generate_csrf_token(self):
        """
        Generate a CSRF token.

        Returns:
            str: The generated CSRF token.

        Usage:
            csrf_token = csrf.generate_csrf_token()
        """
        return secrets.token_hex(32)

    def protect(self, handler):
        """
        Protect a route or view with CSRF token validation.

        Args:
            handler: The route or view function.

        Returns:
            function: The decorated route or view function.

        Usage:
            @app.route('/protected', methods=['POST'])
            @csrf.protect
            def protected_route(request):
                # Your protected route logic here
        """
        @wraps(handler)
        def wrapper(request, **values):
            self._apply_rate_limit(request.remote_addr)
            
            if request.method in ('POST', 'PUT', 'DELETE'):
                submitted_token = request.form.get(self.token_name)
                session_token = request.cookies.get(self.token_name)

                if not submitted_token or submitted_token != session_token:
                    raise Forbidden("CSRF token validation failed.")
            return handler(request, **values)
        return wrapper

    def set_csrf_token_cookie(self, response, token):
        """
        Set the CSRF token as a cookie in the response.

        Args:
            response: The response object.
            token (str): The CSRF token.

        Usage:
            csrf.set_csrf_token_cookie(response, csrf_token)
        """
        response.set_cookie(self.token_name, token, httponly=True, secure=True, samesite='strict', max_age=3600)

    def _apply_rate_limit(self, ip_address):
        now = int(time.time())
        if ip_address not in self.rate_limit_storage:
            self.rate_limit_storage[ip_address] = [(now, 1)]
            return
        
        requests = self.rate_limit_storage[ip_address]
        requests = [r for r in requests if now - r[0] <= self.rate_limit_period]
        requests.append((now, len(requests) + 1))
        
        if len(requests) > self.rate_limit_max_requests:
            raise Forbidden("Rate limit exceeded.")
        
        self.rate_limit_storage[ip_address] = requests
    
    def get_csrf_token(self, request):
        """
        Get the CSRF token from the request's cookies.

        Args:
            request: The request object.

        Returns:
            str: The CSRF token or None if not found.

        Usage:
            csrf_token = csrf.get_csrf_token(request)
        """
        return request.cookies.get(self.token_name)

    def generate_csrf_token_and_set_cookie(self, response):
        """
        Generate a CSRF token, set it as a cookie in the response, and return the token.

        Args:
            response: The response object.

        Returns:
            str: The generated CSRF token.

        Usage:
            csrf_token = csrf.generate_csrf_token_and_set_cookie(response)
        """
        token = self.generate_csrf_token()
        self.set_csrf_token_cookie(response, token)
        return token

    def require_csrf_token(self, request):
        """
        Get and require the CSRF token from the request's cookies.

        Args:
            request: The request object.

        Returns:
            str: The CSRF token.

        Raises:
            Forbidden: If the CSRF token is missing.

        Usage:
            csrf_token = csrf.require_csrf_token(request)
        """
        token = self.get_csrf_token(request)
        if not token:
            raise Forbidden("CSRF token missing.")
        return token

    def validate_csrf_token(self, request):
        """
        Validate the CSRF token in the request's form data against the session token.

        Args:
            request: The request object.

        Returns:
            bool: True if the CSRF token is valid, False otherwise.

        Usage:
            valid = csrf.validate_csrf_token(request)
        """
        submitted_token = request.form.get(self.token_name)
        session_token = self.get_csrf_token(request)
        return submitted_token and submitted_token == session_token

    def csrf_exempt(self, handler):
        """
        Exempt a route or view from CSRF protection.

        Args:
            handler: The route or view function.

        Returns:
            function: The route or view function without CSRF protection.

        Usage:
            @app.route('/unprotected')
            @csrf.csrf_exempt
            def unprotected_route(request):
                # Your unprotected route logic here
        """
        return handler

    def is_csrf_request(self, request):
        """
        Check if the request method is one that requires CSRF protection.

        Args:
            request: The request object.

        Returns:
            bool: True if the request method requires CSRF protection, False otherwise.

        Usage:
            is_csrf = csrf.is_csrf_request(request)
        """
        return request.method in ('POST', 'PUT', 'DELETE')

    def is_same_origin(self, request):
        """
        Check if the request is from the same origin.

        Args:
            request: The request object.

        Returns:
            bool: True if the request is from the same origin, False otherwise.

        Usage:
            same_origin = csrf.is_same_origin(request)
        """
        return True  # Add your same-origin check logic here

    def _get_request_ip(self, request):
        return request.remote_addr

    def _get_session_token(self, request):
        return request.cookies.get(self.token_name)

    def _set_session_token(self, response, token):
        self.set_csrf_token_cookie(response, token)

    def _generate_token(self):
        return self.generate_csrf_token()

    def _clear_session_token(self, response):
        response.delete_cookie(self.token_name)

    def _should_set_cookie(self, request):
        return self.is_same_origin(request) and self.is_csrf_request(request)

    def __call__(self, environ, start_response):
        request = Request(environ)
        environ['csrf'] = self
        return self.app(environ, start_response)
