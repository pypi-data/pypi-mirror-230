import os
import base64
import mimetypes
import json
import importlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.debug import DebuggedApplication
from jinja2 import Environment, FileSystemLoader
from itsdangerous import URLSafeTimedSerializer
from urllib.parse import quote as url_quote, quote_plus as url_quote_plus, urlencode as url_encode
from werkzeug.utils import send_from_directory, safe_join
from werkzeug.local import LocalStack, LocalProxy
from ..components.sessions import SessionManager
from ..components.blueprint import Blueprint
from ..core import pin_error, access_denied

class Emonic:
    """
    Discover a user-friendly Python web framework designed to empower developers in building both standard and high-level applications. Crafted with simplicity in mind, this framework provides an intuitive environment for creating web applications that adhere to industry standards. Whether you're embarking on a straightforward project or aiming for a sophisticated application, our framework streamlines the development process, offering flexibility and tools to match your goals.
    """
    def __init__(self, import_name):
        """
        Initialize the Emonic web application.

        Args:
            import_name (str): The name of the application package.

        Usage:
            app = Emonic(__name__)
        """
        self.template_folder = 'views'
        self.url_map = Map()
        self.static_folder = "static"
        self.error_handlers = {}
        self.middlewares = []
        self.host = 'localhost'
        self.port = 8000
        self.debug = True
        self.secret_key = os.urandom(32)
        self.serializer = URLSafeTimedSerializer(base64.urlsafe_b64encode(self.secret_key))
        self.blueprints = []
        self.import_name = __name__
        self.config = {}
        self.template_backend = 'emonic.backends.EmonicTemplates'
        self.messages = []
        self.principal = None

        self.load_settings()
        self.app_ctx_stack = LocalStack()
        self.g = LocalProxy(lambda: self.app_ctx_stack.top.g)
        self.cookie_jar = {}
        self.session_manager = SessionManager(self.secret_key)
        self.before_request_funcs = []
        self.after_request_funcs = []

    def load_settings(self):
        """
        Load application settings from a settings module.

        Usage:
            app.load_settings()
        """
        try:
            settings_module = importlib.import_module('settings')
            templates_setting = getattr(settings_module, 'TEMPLATES', None)
            self.template_backend = templates_setting[0]['BACKEND'] if templates_setting else self.template_backend
            assert self.template_backend == 'emonic.backends.EmonicTemplates', "This backend isn't supported by Emonic."
            self.template_folder = templates_setting[0]['DIRS'][0] if templates_setting and templates_setting[0]['DIRS'] else self.template_folder
            self.host = getattr(settings_module, 'HOST', self.host)
            self.port = getattr(settings_module, 'PORT', self.port)
            self.debug = getattr(settings_module, 'DEBUG', self.debug)
            self.secret_key = getattr(settings_module, 'SECRET_KEY', self.secret_key)
            self.static_folder = getattr(settings_module, 'STATIC_FOLDER', self.static_folder)
        except ImportError:
            pass
        except (IndexError, KeyError, AssertionError, ValueError) as e:
            raise ValueError("Invalid TEMPLATES setting in settings.py.") from e

        self.template_env = Environment(loader=FileSystemLoader(self.template_folder))

    def add_url_rule(self, rule, endpoint, handler, methods=['GET']):
        """
        Add a URL rule to the application.

        Args:
            rule (str): The URL rule.
            endpoint (str): The endpoint name.
            handler (function): The request handler function.
            methods (list, optional): List of HTTP methods for the rule (default is ['GET']).

        Usage:
            app.add_url_rule('/', 'index', index_handler)
        """
        def view_func(request, **values):
            return handler(request, **values)
        self.url_map.add(Rule(rule, endpoint=endpoint, methods=methods))
        setattr(self, endpoint, view_func)

    def route(self, rule, methods=['GET'], secure=False, pin=None, max_url_length=None, default=None, host=None, strict_slashes=None):
        """
        Create a route decorator for adding URL routes to the application.

        Args:
            rule (str): The URL rule.
            methods (list, optional): List of HTTP methods for the route (default is ['GET']).
            secure (bool, optional): Whether the route requires HTTPS (default is False).
            pin (int, optional): PIN code required for the route (default is None).
            max_url_length (int, optional): Maximum URL length for the route (default is None).
            default (str, optional): Default subdomain for the route (default is None).
            host (str, optional): Host matching rule for the route (default is None).
            strict_slashes (bool, optional): Whether to enforce strict slashes (default is None).

        Usage:
            @app.route('/', methods=['GET'], secure=True, pin=1234)
            def index(request):
                return 'Hello, World!'
        """
        def decorator(handler):
            self.add_url_rule(rule, handler.__name__, handler, methods)

            if max_url_length:
                if len(rule) > max_url_length:
                    raise ValueError(f"Rule exceeds max_url_length of {max_url_length} characters.")

            def secure_handler(request, **values):
                if secure:
                    if request.method == 'GET':
                        response_content = access_denied(request)
                        return Response(response_content, content_type='text/html', status=403)
                    elif request.method == 'POST':
                        user_pin = request.form.get('pin')
                        if int(user_pin) != pin:
                            response_content = pin_error(request)
                            return Response(response_content, content_type='text/html', status=403)

                return handler(request, **values)

            setattr(self, handler.__name__, secure_handler)

            # Apply additional route options
            self.url_map.default_subdomain = default
            self.url_map.host_matching = host
            self.url_map.strict_slashes = strict_slashes

            return secure_handler
        return decorator

    def errorhandler(self, code):
        """
        Create an error handler decorator for handling specific HTTP error codes.

        Args:
            code (int): The HTTP error code.

        Usage:
            @app.errorhandler(404)
            def handle_404(error, request):
                return 'Page not found', 404
        """
        def decorator(handler):
            self.error_handlers[code] = handler
            return handler
        return decorator

    def use(self, middleware):
        """
        Add a middleware to the application.

        Args:
            middleware (function): The middleware function.

        Usage:
            app.use(my_middleware)
        """
        self.middlewares.append(middleware)

    def static_middleware(self, app):
        """
        Create a static file serving middleware for the application.

        Args:
            app (function): The application function.

        Returns:
            function: The middleware function.

        Usage:
            app = app.static_middleware(app)
        """
        def middleware(environ, start_response):
            path = environ['PATH_INFO']
            if path.startswith('/static/'):
                try:
                    filename = path[len('/static/'):]
                    response = self.serve_static(filename)
                    return response(environ, start_response)
                except NotFound:
                    return app(environ, start_response)
            return app(environ, start_response)
        return middleware

    def serve_static(self, filename):
        """
        Serve a static file from the static folder.

        Args:
            filename (str): The name of the static file.

        Returns:
            Response: The response with the static file content.

        Usage:
            response = app.serve_static('css/style.css')
        """
        static_path = os.path.join(self.static_folder, filename)
        if os.path.isfile(static_path):
            mimetype, _ = mimetypes.guess_type(static_path)
            if mimetype:
                return Response(open(static_path, 'rb').read(), mimetype=mimetype)
        raise NotFound()

    def register_blueprint(self, blueprint):
        """
        Register a blueprint with the application.

        Args:
            blueprint (Blueprint): The blueprint to register.

        Usage:
            app.register_blueprint(my_blueprint)
        """
        self.blueprints.append(blueprint)

    def handle_request(self, request):
        """
        Handle an incoming HTTP request.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: The response to the request.

        Usage:
            response = app.handle_request(request)
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(self, endpoint)

            # Execute before_request functions
            response = self.preprocess_request(request)
            if response:
                return response

            # Handle the actual request
            handler_response = handler(request, **values)

            # Execute after_request functions
            response = self.postprocess_request(request, handler_response)

            # Automatically handle response format based on returned value
            if isinstance(response, str):
                # Check if the response is HTML
                if response.startswith("<"):
                    response = Response(response, content_type='text/html')
                # Check if the response is XML
                elif response.startswith("<?xml"):
                    response = Response(response, content_type='application/xml')
                # Check if the response is CSV
                elif response.startswith("data:text/csv"):
                    response = Response(response, content_type='text/csv')
                # Check if the response is PDF
                elif response.startswith("%PDF-"):
                    response = Response(response, content_type='application/pdf')
                # Check if the response is an RSS feed
                elif "<rss" in response.lower():
                    response = Response(response, content_type='application/rss+xml')
                # Check if the response is CSS
                elif response.startswith("/*"):
                    response = Response(response, content_type='text/css')
                else:
                    response = Response(response, content_type='text/plain')
            elif isinstance(response, dict):
                response = Response(json.dumps(response), content_type='application/json')
            response.headers['Framework'] = 'Emonic/1.0.2'
            return response

        except NotFound as e:
            response = self.handle_error(404, e, request)
        except HTTPException as e:
            response = e
        return response

    def handle_error(self, code, error, request):
        """
        Handle an HTTP error with a registered error handler.

        Args:
            code (int): The HTTP error code.
            error (HTTPException): The HTTP error exception.
            request (Request): The incoming request object.

        Returns:
            Response: The response to the error.

        Usage:
            response = app.handle_error(404, not_found_error, request)
        """
        handler = self.error_handlers.get(code)
        if handler:
            return handler(error, request)
        else:
            return error

    def before_request(self, func):
        """
        Register a function to be executed before each request.

        Args:
            func (function): The function to be executed.

        Usage:
            @app.before_request
            def my_before_request(request):
                # Do something before each request
        """
        self.before_request_funcs.append(func)
        return func

    def after_request(self, func):
        """
        Register a function to be executed after each request.

        Args:
            func (function): The function to be executed.

        Usage:
            @app.after_request
            def my_after_request(request, response):
                # Do something after each request
                return response
        """
        self.after_request_funcs.append(func)
        return func

    def preprocess_request(self, request):
        """
        Execute all registered before_request functions.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: The response from a before_request function, if any.

        Usage:
            response = app.preprocess_request(request)
        """
        for func in self.before_request_funcs:
            response = func(request)
            if response:
                return response

    def postprocess_request(self, request, response):
        """
        Execute all registered after_request functions.

        Args:
            request (Request): The incoming request object.
            response (Response): The response to the request.

        Returns:
            Response: The final response after all after_request functions.

        Usage:
            response = app.postprocess_request(request, response)
        """
        for func in self.after_request_funcs:
            response = func(request, response)
        return response

    def wsgi_app(self, environ, start_response):
        """
        WSGI application for handling requests and responses.

        Args:
            environ (dict): The WSGI environment.
            start_response (function): The start_response function.

        Returns:
            Response: The response to the request.

        Usage:
            app = Emonic(__name__)
            response = app.wsgi_app(environ, start_response)
        """
        request = Request(environ)
        for blueprint in self.blueprints:
            if request.path.startswith(blueprint.url_prefix):
                request.blueprint = blueprint
                response = blueprint.wsgi_app(environ, start_response)
                return response

        session_id = request.cookies.get('session_id')
        session_data_str = self.session_manager.load_session(session_id)

        # Deserialize the session data from JSON
        if session_data_str:
            session_data = json.loads(session_data_str)
        else:
            session_data = {}

        request.session = session_data
        response = self.handle_request(request)

        # Serialize the session data to JSON before saving
        serialized_session = json.dumps(request.session)
        session_id = self.session_manager.save_session(serialized_session)

        # Set session expiration to 1 hour by default
        session_expiration = datetime.now() + self.session_manager.session_lifetime

        if isinstance(response, Response):
            response.set_cookie('session_id', session_id['session_id'], expires=session_expiration, secure=True, httponly=True)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        """
        Call the WSGI application.

        Args:
            environ (dict): The WSGI environment.
            start_response (function): The start_response function.

        Returns:
            Response: The response to the request.

        Usage:
            app = Emonic(__name__)
            response = app(environ, start_response)
        """
        app = self.wsgi_app
        for middleware in reversed(self.middlewares):
            app = middleware(app)
        app = self.static_middleware(app)  # Add the static file serving middleware
        return app(environ, start_response)

    def run(self, host=None, port=None, debug=None, secret_key=None,
            threaded=True, processes=1, ssl_context=None, use_reloader=True, use_evalex=True):
        """
        Run the Emonic application using the Werkzeug development server.

        Args:
            host (str, optional): The hostname or IP address to listen on (default is 'localhost').
            port (int, optional): The port number to listen on (default is 8000).
            debug (bool, optional): Enable or disable debug mode (default is True).
            secret_key (str, optional): The secret key for the application (default is randomly generated).
            threaded (bool, optional): Enable or disable threaded mode (default is True).
            processes (int, optional): Number of processes to spawn (default is 1).
            ssl_context (object, optional): An SSL context for serving over HTTPS (default is None).
            use_reloader (bool, optional): Enable or disable the reloader (default is True).
            use_evalex (bool, optional): Enable or disable the exception evaluation feature (default is True).

        Usage:
            app.run(host='0.0.0.0', port=8080, debug=True)
        """
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if debug is not None:
            self.debug = debug
        if secret_key is not None:
            self.secret_key = secret_key

        if self.debug:
            app = DebuggedApplication(self, evalex=use_evalex)
        else:
            app = self

        from werkzeug.serving import run_simple
        run_simple(self.host, self.port, app,
                    use_reloader=use_reloader,
                    threaded=threaded, processes=processes, ssl_context=ssl_context)

    def parallel_handler(self, handler):
        """
        Create a decorator to execute a request handler in parallel using ThreadPoolExecutor.

        Args:
            handler (function): The request handler function.

        Returns:
            function: The decorator for parallel execution.

        Usage:
            @app.parallel_handler
            def my_handler(request):
                # Perform parallel tasks
                return result
        """
        def wrapper(request, **values):
            # Execute the handler using ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor() as executor:
                future = executor.submit(handler, request, **values)
                return future.result()  # Get the result of the handler

        return wrapper

    def g(self):
        """
        Access the 'g' object associated with the current application context.

        Returns:
            dict: The 'g' object.

        Usage:
            g = app.g()
        """
        ctx = self.app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'g'):
                ctx.g = {}
            return ctx.g

    def current_app(self):
        """
        Return the current application instance.

        Returns:
            Emonic: The current application instance.

        Usage:
            current_app = app.current_app()
        """
        return self

    def _get_g(self):
        """
        Access the 'g' object associated with the current application context.

        Returns:
            dict: The 'g' object.

        Usage:
            g = app._get_g()
        """
        ctx = self.app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, 'g'):
                ctx.g = {}
            return ctx.g

    def parse_date(date_string):
        """
        Parse a date string into a datetime object.

        Args:
            date_string (str): The date string to parse.

        Returns:
            datetime: The parsed datetime object.

        Usage:
            parsed_date = app.parse_date('Tue, 31 Aug 2023 10:15:30 GMT')
        """
        return datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %Z')

    def is_resource_modified(self, request, filename, etag=None):
        """
        Check if a resource has been modified based on ETag or If-Modified-Since headers.

        Args:
            request (Request): The incoming request object.
            filename (str): The filename of the resource.
            etag (str, optional): The ETag value for the resource (default is None).

        Returns:
            bool: True if the resource has been modified, False otherwise.

        Usage:
            modified = app.is_resource_modified(request, 'path/to/resource.txt', etag='123456')
        """
        file_size = os.path.getsize(filename)
        mtime = int(os.path.getmtime(filename))
        etag = etag or (file_size, mtime)
        if_none_match = request.headers.get('If-None-Match')
        if if_none_match:
            return etag != if_none_match
        if_modified_since = request.headers.get('If-Modified-Since')
        if if_modified_since:
            if_modified_since = self.parse_date(if_modified_since)
            return datetime.utcfromtimestamp(mtime) > if_modified_since
        return True
