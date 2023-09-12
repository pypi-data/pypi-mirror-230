import logging
from werkzeug.wrappers import Response

class CORS:
    def __init__(
        self,
        allowed_origins='*',
        allowed_methods=None,
        max_age=3600,
        allowed_headers=None,
        expose_headers=None,
        allow_credentials=False,
        cors_profile='default',
        validate_request_origin=None,
        log_cors_requests=False,
        cors_logger_name='cors',
    ):
        """
        Initialize the CORS middleware.

        Args:
            allowed_origins (str, list, or callable): Allowed origins.
            allowed_methods (list): Allowed HTTP methods.
            max_age (int): Maximum age of preflight request result.
            allowed_headers (list): Allowed request headers.
            expose_headers (list): Headers exposed to the response.
            allow_credentials (bool): Allow credentials in requests.
            cors_profile (str): CORS profile (default or wildcard).
            validate_request_origin (str, list, callable, or None): Validation function for request origin.
            log_cors_requests (bool): Log CORS requests.
            cors_logger_name (str): Name of the CORS logger.

        Usage:
            cors = CORS(allowed_origins='*', allowed_methods=['GET'], max_age=3600)
        """
        self.allowed_origins = allowed_origins
        self.allowed_methods = allowed_methods
        self.max_age = max_age
        self.allowed_headers = allowed_headers
        self.expose_headers = expose_headers
        self.allow_credentials = allow_credentials
        self.cors_profile = cors_profile
        self._validate_request_origin = validate_request_origin
        self.log_cors_requests = log_cors_requests
        self.cors_logger_name = cors_logger_name
        self.cors_logger = logging.getLogger(cors_logger_name)

    def handle_preflight(self, request):
        """
        Handle preflight requests.

        Args:
            request: The incoming request.

        Returns:
            Response: The response to the preflight request.

        Usage:
            response = cors.handle_preflight(request)
        """
        response = Response('', status=204)
        response.headers.update(self._build_cors_headers())
        return response

    def enable(self):
        """
        Enable CORS for a Flask route.

        Usage:
            @app.route('/example')
            @cors.enable()
            def example():
                return 'Hello, CORS!'
        """
        def decorator(handler):
            def wrapper(request, **values):
                if not self.validate_request_origin(request):
                    self.cors_logger.warning('Request origin not allowed: %s', request.headers.get('Origin'))
                    return self._handle_error('Forbidden', status_code=403)

                if self.log_cors_requests:
                    self.log_cors_request(request.headers.get('Origin'))

                response = handler(request, **values)

                if request.method == 'OPTIONS':
                    return self.preflight_response()

                if isinstance(response, Response):
                    response.headers.update(self._build_cors_headers())
                    return response

                response = Response(response, content_type='text/plain')
                response.headers.update(self._build_cors_headers())
                return response

            return wrapper

        return decorator

    def _build_cors_headers(self):
        cors_headers = {
            'Access-Control-Allow-Origin': self.allowed_origins,
            'Access-Control-Allow-Methods': ', '.join(self.allowed_methods or []),
            'Access-Control-Max-Age': str(self.max_age)
        }
        if self.allowed_headers:
            cors_headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
        if self.expose_headers:
            cors_headers['Access-Control-Expose-Headers'] = ', '.join(self.expose_headers)
        if self.allow_credentials:
            cors_headers['Access-Control-Allow-Credentials'] = 'true'
        return cors_headers

    def _handle_error(self, error_message, status_code=400):
        response = Response(error_message, status=status_code)
        response.headers.update(self._build_cors_headers())
        return response

    def handle_error(self, error_message, status_code=400):
        """
        Handle CORS-related errors.

        Args:
            error_message (str): The error message.
            status_code (int): The HTTP status code.

        Returns:
            Response: The response to the error.

        Usage:
            response = cors.handle_error('Forbidden', status_code=403)
        """
        return self._handle_error(error_message, status_code)

    def set_allowed_origins(self, origins):
        """
        Set allowed origins.

        Args:
            origins (str, list, or callable): Allowed origins.

        Usage:
            cors.set_allowed_origins(['http://example.com', 'https://example.org'])
        """
        self.allowed_origins = origins

    def set_allowed_methods(self, methods):
        """
        Set allowed HTTP methods.

        Args:
            methods (list): Allowed HTTP methods.

        Usage:
            cors.set_allowed_methods(['GET', 'POST'])
        """
        self.allowed_methods = methods

    def set_allowed_headers(self, headers):
        """
        Set allowed request headers.

        Args:
            headers (list): Allowed request headers.

        Usage:
            cors.set_allowed_headers(['Authorization', 'Content-Type'])
        """
        self.allowed_headers = headers

    def set_expose_headers(self, headers):
        """
        Set headers exposed to the response.

        Args:
            headers (list): Headers exposed to the response.

        Usage:
            cors.set_expose_headers(['X-Custom-Header'])
        """
        self.expose_headers = headers

    def set_allow_credentials(self, allow):
        """
        Set whether to allow credentials in requests.

        Args:
            allow (bool): Allow credentials.

        Usage:
            cors.set_allow_credentials(True)
        """
        self.allow_credentials = allow

    def set_max_age(self, age):
        """
        Set the maximum age of preflight request result.

        Args:
            age (int): Maximum age in seconds.

        Usage:
            cors.set_max_age(3600)
        """
        self.max_age = age

    def set_cors_logger_name(self, logger_name):
        """
        Set the name of the CORS logger.

        Args:
            logger_name (str): Name of the logger.

        Usage:
            cors.set_cors_logger_name('my_cors_logger')
        """
        self.cors_logger_name = logger_name
        self.cors_logger = logging.getLogger(logger_name)

    def validate_request_origin(self, request):
        """
        Validate the request origin.

        Args:
            request: The incoming request.

        Returns:
            bool: True if the request origin is allowed, False otherwise.

        Usage:
            def origin_validator(request):
                return request.headers.get('Origin') == 'http://example.com'
            
            cors.set_validate_request_origin(origin_validator)
        """
        if callable(self._validate_request_origin):
            return self._validate_request_origin(request)
        elif self._validate_request_origin is None or self._validate_request_origin == '*':
            return True
        elif isinstance(self._validate_request_origin, (list, tuple)):
            return request.headers.get('Origin') in self._validate_request_origin
        return False

    def log_cors_request(self, origin):
        """
        Log CORS requests.

        Args:
            origin (str): The origin of the request.

        Usage:
            cors.log_cors_request('http://example.com')
        """
        self.cors_logger.info('CORS request from origin: %s', origin)

    def preflight_response(self):
        """
        Create a preflight response.

        Returns:
            Response: The preflight response.

        Usage:
            response = cors.preflight_response()
        """
        response = Response('', status=204)
        response.headers.update(self._build_cors_headers())
        return response

    def custom_response(self, content, content_type='text/plain', status_code=200):
        """
        Create a custom CORS-enabled response.

        Args:
            content (str): The response content.
            content_type (str): The content type.
            status_code (int): The HTTP status code.

        Returns:
            Response: The custom CORS-enabled response.

        Usage:
            response = cors.custom_response('Custom Response', content_type='text/html', status_code=200)
        """
        response = Response(content, content_type=content_type, status=status_code)
        response.headers.update(self._build_cors_headers())
        return response
    
    def set_validate_request_origin(self, validation_function):
        """
        Set a custom validation function for request origin.

        Args:
            validation_function (callable): The validation function.

        Usage:
            cors.set_validate_request_origin(custom_origin_validator)
        """
        self.validate_request_origin = validation_function

    def add_allowed_origin(self, origin):
        """
        Add an allowed origin.

        Args:
            origin (str): The allowed origin to add.

        Usage:
            cors.add_allowed_origin('http://example.com')
        """
        if self.allowed_origins == '*':
            self.allowed_origins = []
        if origin not in self.allowed_origins:
            self.allowed_origins.append(origin)

    def remove_allowed_origin(self, origin):
        """
        Remove an allowed origin.

        Args:
            origin (str): The allowed origin to remove.

        Usage:
            cors.remove_allowed_origin('http://example.com')
        """
        if origin in self.allowed_origins:
            self.allowed_origins.remove(origin)

    def add_allowed_method(self, method):
        """
        Add an allowed HTTP method.

        Args:
            method (str): The allowed HTTP method to add.

        Usage:
            cors.add_allowed_method('PUT')
        """
        if self.allowed_methods is None:
            self.allowed_methods = []
        if method not in self.allowed_methods:
            self.allowed_methods.append(method)

    def remove_allowed_method(self, method):
        """
        Remove an allowed HTTP method.

        Args:
            method (str): The allowed HTTP method to remove.

        Usage:
            cors.remove_allowed_method('PUT')
        """
        if self.allowed_methods is not None and method in self.allowed_methods:
            self.allowed_methods.remove(method)

    def add_allowed_header(self, header):
        """
        Add an allowed request header.

        Args:
            header (str): The allowed request header to add.

        Usage:
            cors.add_allowed_header('Authorization')
        """
        if self.allowed_headers is None:
            self.allowed_headers = []
        if header not in self.allowed_headers:
            self.allowed_headers.append(header)

    def remove_allowed_header(self, header):
        """
        Remove an allowed request header.

        Args:
            header (str): The allowed request header to remove.

        Usage:
            cors.remove_allowed_header('Authorization')
        """
        if self.allowed_headers is not None and header in self.allowed_headers:
            self.allowed_headers.remove(header)
            
    def add_exposed_header(self, header):
        """
        Add an exposed response header.

        Args:
            header (str): The exposed response header to add.

        Usage:
            cors.add_exposed_header('X-Custom-Header')
        """
        if self.expose_headers is None:
            self.expose_headers = []
        if header not in self.expose_headers:
            self.expose_headers.append(header)

    def remove_exposed_header(self, header):
        """
        Remove an exposed response header.

        Args:
            header (str): The exposed response header to remove.

        Usage:
            cors.remove_exposed_header('X-Custom-Header')
        """
        if self.expose_headers is not None and header in self.expose_headers:
            self.expose_headers.remove(header)
            
    def set_cors_profile(self, profile):
        """
        Set the CORS profile.

        Args:
            profile (str): The CORS profile ('default' or 'wildcard').

        Usage:
            cors.set_cors_profile('wildcard')
        """
        self.cors_profile = profile

    def enable_logging(self, logger_name='cors'):
        """
        Enable CORS request logging.

        Args:
            logger_name (str): Name of the CORS logger.

        Usage:
            cors.enable_logging('my_cors_logger')
        """
        self.log_cors_requests = True
        self.cors_logger_name = logger_name
        self.cors_logger = logging.getLogger(logger_name)

    def disable_logging(self):
        """
        Disable CORS request logging.

        Usage:
            cors.disable_logging()
        """
        self.log_cors_requests = False
        self.cors_logger_name = ''
        self.cors_logger = None
        
    def set_logger_level(self, level):
        """
        Set the CORS logger's logging level.

        Args:
            level (int): The logging level.

        Usage:
            cors.set_logger_level(logging.DEBUG)
        """
        if self.cors_logger:
            self.cors_logger.setLevel(level)

    def enable_all_methods(self):
        """
        Enable all HTTP methods.

        Usage:
            cors.enable_all_methods()
        """
        self.allowed_methods = ['OPTIONS', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    def enable_all_headers(self):
        """
        Enable all request headers and exposed headers.

        Usage:
            cors.enable_all_headers()
        """
        self.allowed_headers = None  # Allows all headers
        self.expose_headers = None  # Exposes all headers

    def disable_credentials(self):
        """
        Disable credentials in requests.

        Usage:
            cors.disable_credentials()
        """
        self.allow_credentials = False

    def disable_preflight_cache(self):
        """
        Disable preflight request caching.

        Usage:
            cors.disable_preflight_cache()
        """
        self.max_age = 0
        
    def set_max_age_minutes(self, minutes):
        """
        Set the maximum age of preflight request result in minutes.

        Args:
            minutes (int): Maximum age in minutes.

        Usage:
            cors.set_max_age_minutes(30)
        """
        self.max_age = minutes * 60

    def add_custom_header(self, key, value):
        """
        Add a custom response header.

        Args:
            key (str): The header key.
            value (str): The header value.

        Usage:
            cors.add_custom_header('X-Custom-Header', 'Custom-Value')
        """
        if self.custom_headers is None:
            self.custom_headers = {}
        self.custom_headers[key] = value

    def remove_custom_header(self, key):
        """
        Remove a custom response header.

        Args:
            key (str): The header key to remove.

        Usage:
            cors.remove_custom_header('X-Custom-Header')
        """
        if self.custom_headers is not None and key in self.custom_headers:
            del self.custom_headers[key]
    
    def set_cors_origin_validator(self, origin_validator):
        """
        Set a custom origin validator function.

        Args:
            origin_validator (callable): The origin validator function.

        Usage:
            cors.set_cors_origin_validator(custom_origin_validator)
        """
        self.cors_origin_validator = origin_validator

    def set_expose_all_headers(self, expose_all=True):
        """
        Set whether to expose all headers in responses.

        Args:
            expose_all (bool): True to expose all headers, False to expose none.

        Usage:
            cors.set_expose_all_headers(True)
        """
        if expose_all:
            self.expose_headers = None  # Expose all headers
        else:
            self.expose_headers = []

    def set_response_headers(self, headers):
        """
        Set custom response headers.

        Args:
            headers (dict): Custom response headers.

        Usage:
            cors.set_response_headers({'X-Custom-Header': 'Custom-Value'})
        """
        self.response_headers = headers

    def clear_response_headers(self):
        """
        Clear custom response headers.

        Usage:
            cors.clear_response_headers()
        """
        self.response_headers = {}
        
    def enable_same_site_cookies(self, same_site_policy='Lax'):
        """
        Enable same-site cookies with the specified policy.

        Args:
            same_site_policy (str): The same-site policy ('Lax' or 'Strict').

        Usage:
            cors.enable_same_site_cookies('Lax')
        """
        self.same_site_cookies = same_site_policy

    def set_cors_max_age(self, max_age_seconds):
        """
        Set the maximum age of preflight request result in seconds.

        Args:
            max_age_seconds (int): Maximum age in seconds.

        Usage:
            cors.set_cors_max_age(1800)
        """
        self.max_age = max_age_seconds

    def set_cors_allowed_origins(self, origins):
        """
        Set allowed origins.

        Args:
            origins (str, list, or callable): Allowed origins.

        Usage:
            cors.set_cors_allowed_origins(['http://example.com', 'https://example.org'])
        """
        self.allowed_origins = origins

    def set_cors_allowed_methods(self, methods):
        """
        Set allowed HTTP methods.

        Args:
            methods (list): Allowed HTTP methods.

        Usage:
            cors.set_cors_allowed_methods(['GET', 'POST'])
        """
        self.allowed_methods = methods
