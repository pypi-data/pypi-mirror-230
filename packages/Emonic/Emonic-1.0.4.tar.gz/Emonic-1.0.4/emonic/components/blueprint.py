from werkzeug.routing import Map, Rule
from werkzeug.exceptions import NotFound
from werkzeug.wrappers import Request, Response
from .sessions import session_manager
from ..components import pin_error, access_denied
import json
import os

class Blueprint:
    def __init__(self, name, import_name, url_prefix=''):
        """
        Initialize a Blueprint.

        Args:
            name (str): The name of the Blueprint.
            import_name (str): The name of the module where the Blueprint is located.
            url_prefix (str, optional): The URL prefix for routes defined in the Blueprint.

        Usage:
            my_blueprint = Blueprint('my_blueprint', __name__, url_prefix='/my_prefix')
        """
        self.name = name
        self.import_name = import_name
        self.url_prefix = url_prefix
        self.url_map = Map()
        self.error_handlers = {}
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.session_manager = session_manager

    def add_url_rule(self, rule, endpoint, handler, methods=['GET']):
        """
        Add a URL rule to the Blueprint.

        Args:
            rule (str): The URL rule.
            endpoint (str): The endpoint name.
            handler (function): The request handler function.
            methods (list, optional): The HTTP methods allowed for this route (default is ['GET']).

        Usage:
            my_blueprint.add_url_rule('/my_route', 'my_endpoint', my_handler, methods=['GET', 'POST'])
        """
        rule = self.url_prefix + rule
        self.url_map.add(Rule(rule, endpoint=endpoint, methods=methods))
        setattr(self, endpoint, handler)

    def route(self, rule, methods=['GET'], secure=False, pin=None, max_url_length=None, default=None, host=None, strict_slashes=None):
        """
        Define a route for the Blueprint.

        Args:
            rule (str): The URL rule.
            methods (list, optional): The HTTP methods allowed for this route (default is ['GET']).
            secure (bool, optional): Whether the route should be secure (default is False).
            pin (int, optional): PIN for secure routes.
            max_url_length (int, optional): Maximum URL length.
            default (str, optional): Default subdomain.
            host (bool, optional): Enable host matching.
            strict_slashes (bool, optional): Enable strict slashes.

        Usage:
            @my_blueprint.route('/my_route', methods=['GET', 'POST'], secure=True, pin=1234)
            def my_secure_handler(request):
                return Response('Secure Route')

            @my_blueprint.route('/long_url', max_url_length=50)
            def my_long_url_handler(request):
                return Response('Long URL Route')
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
        Register an error handler for a specific HTTP status code.

        Args:
            code (int): The HTTP status code.

        Usage:
            @my_blueprint.errorhandler(404)
            def handle_404_error(error):
                return Response('Not Found', status=404)
        """
        def decorator(handler):
            self.error_handlers[code] = handler
            return handler
        return decorator

    def before_request(self, func):
        """
        Register a function to be executed before each request.

        Args:
            func (function): The before-request function.

        Usage:
            @my_blueprint.before_request
            def my_before_request(request):
                # Do something before the request
        """
        self.before_request_funcs.append(func)
        return func

    def after_request(self, func):
        """
        Register a function to be executed after each request.

        Args:
            func (function): The after-request function.

        Usage:
            @my_blueprint.after_request
            def my_after_request(request, response):
                # Do something after the request and response
                return response
        """
        self.after_request_funcs.append(func)
        return func

    def preprocess_request(self, request):
        """
        Execute all registered before-request functions.

        Args:
            request: The request object.

        Usage:
            self.preprocess_request(request)
        """
        for func in self.before_request_funcs:
            func(request)

    def postprocess_response(self, request, response):
        """
        Execute all registered after-request functions.

        Args:
            request: The request object.
            response: The response object.

        Usage:
            response = self.postprocess_response(request, response)
        """
        for func in self.after_request_funcs:
            response = func(request, response)
        return response

    def handle_request(self, request):
        """
        Handle an incoming request.

        Args:
            request: The request object.

        Returns:
            Response: The response object.

        Usage:
            response = self.handle_request(request)
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(self, endpoint)
            response = handler(request, **values)
        except NotFound as e:
            response = self.handle_error(404, e)
        return response

    def handle_error(self, code, error):
        """
        Handle an error response.

        Args:
            code (int): The HTTP status code.
            error: The error object.

        Returns:
            Response: The error response.

        Usage:
            response = self.handle_error(404, 'Not Found')
        """
        handler = self.error_handlers.get(code)
        if handler:
            return handler(error)
        else:
            response = Response(str(error), status=code)
            response.set_cookie('session_id', '', expires=0)
            return response

    def wsgi_app(self, environ, start_response):
        """
        WSGI application.

        Args:
            environ: The WSGI environment.
            start_response: The start_response function.

        Returns:
            Response: The response object.

        Usage:
            app = Blueprint('my_app', __name__)
            wsgi_app = app.wsgi_app
        """
        request = Request(environ)
        session_id = request.cookies.get('session_id')
        session_data = self.session_manager.load_session(session_id)
        
        if session_data:
            session_data = json.loads(session_data)

        request.session = session_data
        self.preprocess_request(request)
        response = self.handle_request(request)
        response = self.postprocess_response(request, response)

        serialized_session = json.dumps(request.session)
        session_id = self.session_manager.save_session(serialized_session)

        if isinstance(response, Response):
            response.set_cookie('session_id', session_id['session_id'], secure=True, httponly=True)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def json_response(self, data, status=200):
        """
        Create a JSON response.

        Args:
            data: The JSON data.
            status (int, optional): The HTTP status code (default is 200).

        Returns:
            Response: The JSON response.

        Usage:
            response = my_blueprint.json_response({'key': 'value'}, status=200)
        """
        return Response(json.dumps(data), status=status, content_type='application/json')

    def redirect(self, location, status=302):
        """
        Create a redirect response.

        Args:
            location (str): The URL to redirect to.
            status (int, optional): The HTTP status code (default is 302).

        Returns:
            Response: The redirect response.

        Usage:
            response = my_blueprint.redirect('/new_location', status=302)
        """
        response = Response(status=status)
        response.headers['Location'] = location
        return response

    def static_file(self, filename):
        """
        Serve a static file.

        Args:
            filename (str): The name of the static file.

        Returns:
            Response: The response with the static file.

        Usage:
            response = my_blueprint.static_file('my_static_file.txt')
        """
        static_dir = os.path.join(os.path.dirname(self.import_name), 'static')
        file_path = os.path.join(static_dir, filename)
        
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            return Response(content, content_type='application/octet-stream')
        else:
            return self.handle_error(404, f'Static file "{filename}" not found')

    def add_error_handler(self, code, handler):
        """
        Add a custom error handler.

        Args:
            code (int): The HTTP status code.
            handler: The error handler function.

        Usage:
            my_blueprint.add_error_handler(404, custom_error_handler)
        """
        self.error_handlers[code] = handler

    def add_middleware(self, middleware_func):
        """
        Add a middleware function to be executed before requests.

        Args:
            middleware_func (function): The middleware function.

        Usage:
            my_blueprint.add_middleware(my_middleware)
        """
        self.before_request_funcs.append(middleware_func)

    def add_after_request(self, after_request_func):
        """
        Add a function to be executed after requests.

        Args:
            after_request_func (function): The after-request function.

        Usage:
            my_blueprint.add_after_request(my_after_request)
        """
        self.after_request_funcs.append(after_request_func)

    def render_template(self, template_name, **context):
        """
        Render a Jinja2 template.

        Args:
            template_name (str): The name of the template.
            **context: Additional context data.

        Returns:
            Response: The rendered template as a response.

        Usage:
            response = my_blueprint.render_template('my_template.html', key1='value1', key2='value2')
        """
        template_dir = os.path.join(os.path.dirname(self.import_name), 'templates')
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_name)
        return Response(template.render(context), content_type='text/html')

    def text_response(self, content, status=200):
        """
        Create a plain text response.

        Args:
            content (str): The plain text content.
            status (int, optional): The HTTP status code (default is 200).

        Returns:
            Response: The text response.

        Usage:
            response = my_blueprint.text_response('Hello, World!', status=200)
        """
        return Response(content, status=status, content_type='text/plain')

    def html_response(self, content, status=200):
        """
        Create an HTML response.

        Args:
            content (str): The HTML content.
            status (int, optional): The HTTP status code (default is 200).

        Returns:
            Response: The HTML response.

        Usage:
            response = my_blueprint.html_response('<html><body>Hello, World!</body></html>', status=200)
        """
        return Response(content, status=status, content_type='text/html')

    def set_cookie(self, key, value, **options):
        """
        Set a cookie in the response.

        Args:
            key (str): The name of the cookie.
            value (str): The value to set for the cookie.
            **options: Additional cookie options (e.g., expires, secure, httponly).

        Returns:
            Response: The response with the set cookie.

        Usage:
            response = my_blueprint.set_cookie('my_cookie', 'cookie_value', expires=3600, secure=True, httponly=True)
        """
        response = Response()
        response.set_cookie(key, value, **options)
        return response

    def clear_cookie(self, key, **options):
        """
        Clear a cookie in the response.

        Args:
            key (str): The name of the cookie to clear.
            **options: Additional cookie options (e.g., expires, secure, httponly).

        Returns:
            Response: The response with the cleared cookie.

        Usage:
            response = my_blueprint.clear_cookie('my_cookie', expires=0, secure=True, httponly=True)
        """
        response = Response()
        response.delete_cookie(key, **options)
        return response

    def json_error_response(self, message, status=400):
        """
        Create a JSON error response.

        Args:
            message (str): The error message.
            status (int, optional): The HTTP status code (default is 400).

        Returns:
            Response: The JSON error response.

        Usage:
            response = my_blueprint.json_error_response('Invalid input', status=400)
        """
        error_data = {'error': message}
        return self.json_response(error_data, status)

    def xml_response(self, content, status=200):
        """
        Create an XML response.

        Args:
            content (str): The XML content.
            status (int, optional): The HTTP status code (default is 200).

        Returns:
            Response: The XML response.

        Usage:
            response = my_blueprint.xml_response('<root><item>Content</item></root>', status=200)
        """
        return Response(content, status=status, content_type='application/xml')

    def file_response(self, file_path, attachment_filename=None):
        """
        Create a file download response.

        Args:
            file_path (str): The path to the file to be downloaded.
            attachment_filename (str, optional): The filename for the downloaded file.

        Returns:
            Response: The file download response.

        Usage:
            response = my_blueprint.file_response('/path/to/my_file.txt', attachment_filename='downloaded.txt')
        """
        if not os.path.isfile(file_path):
            return self.json_error_response('File not found', status=404)

        with open(file_path, 'rb') as f:
            content = f.read()

        response = Response(content, content_type='application/octet-stream')
        if attachment_filename:
            response.headers['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
        return response
