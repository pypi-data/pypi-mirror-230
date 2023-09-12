from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound, MethodNotAllowed, BadRequest
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.middleware.profiler import ProfilerMiddleware
import json
from xml.etree import ElementTree as ET
from .requestParser import RequestParser

class Restful:
    def __init__(self):
        """
        Initialize a RESTful API.

        :return: None
        """
        self.url_map = Map()
        self.resources = {}
        self.middlewares = []
        self.error_handlers = {}
        self.debug = False

    def route(self, rule, **options):
        """
        Define a route for a resource.

        :param rule: The route URL pattern.
        :param options: Additional route options.
        :return: A decorator function.
        """
        def decorator(func):
            endpoint = func.__name__
            rule_obj = Rule(rule, endpoint=endpoint, **options)
            self.url_map.add(rule_obj)
            self.resources[endpoint] = func
            return func

        return decorator

    def get(self, rule, **options):
        """
        Define a GET route for a resource.

        :param rule: The route URL pattern.
        :param options: Additional route options.
        :return: A decorator function.
        """
        return self.route(rule, methods=['GET'], **options)

    def post(self, rule, **options):
        """
        Define a POST route for a resource.

        :param rule: The route URL pattern.
        :param options: Additional route options.
        :return: A decorator function.
        """
        return self.route(rule, methods=['POST'], **options)

    def put(self, rule, **options):
        """
        Define a PUT route for a resource.

        :param rule: The route URL pattern.
        :param options: Additional route options.
        :return: A decorator function.
        """
        return self.route(rule, methods=['PUT'], **options)

    def delete(self, rule, **options):
        """
        Define a DELETE route for a resource.

        :param rule: The route URL pattern.
        :param options: Additional route options.
        :return: A decorator function.
        """
        return self.route(rule, methods=['DELETE'], **options)

    def add_resource(self, resource_class, route, endpoint=None, **kwargs):
        """
        Add a resource with routing to the API.

        :param resource_class: The resource class to add.
        :param route: The route URL for the resource.
        :param endpoint: The endpoint name for the resource (default is None).
        :param kwargs: Additional options for adding the resource.
        """
        resource = resource_class(self, **kwargs)
        if endpoint is None:
            endpoint = resource.__class__.__name__.lower()
        rule_obj = Rule(route, endpoint=endpoint)
        self.url_map.add(rule_obj)
        self.resources[endpoint] = resource

    def errorhandler(self, code):
        """
        Define an error handler for a specific HTTP status code.

        :param code: The HTTP status code to handle.
        :return: A decorator function.
        """
        def decorator(func):
            self.add_error_handler(code, func)
            return func
        return decorator

    def use_args(self, **kwargs):
        """
        Define request argument parsing using the RequestParser.

        :param kwargs: Request argument configuration.
        :return: A decorator function.
        """
        def decorator(func):
            request_parser = self.parser
            for name, config in kwargs.items():
                request_parser.add_argument(name, **config)

            @self.app.use_args(request_parser)
            def wrapped_func(request, args, **kwargs):
                return func(request, args, **kwargs)

            return wrapped_func

        return decorator

    def use_kwargs(self, **kwargs):
        """
        Define request keyword argument parsing using the RequestParser.

        :param kwargs: Request argument configuration.
        :return: A decorator function.
        """
        def decorator(func):
            request_parser = self.parser
            for name, config in kwargs.items():
                request_parser.add_argument(name, **config)

            @self.app.use_kwargs(request_parser)
            def wrapped_func(request, **kwargs):
                return func(request, **kwargs)

            return wrapped_func
        return decorator

    def dispatch_request(self, request):
        """
        Dispatch an HTTP request to the appropriate resource.

        :param request: The HTTP request object.
        :return: The HTTP response.
        """
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            resource = self.resources.get(endpoint)
            if resource:
                if request.method == 'OPTIONS':
                    return self.handle_options(resource)
                response_data = resource.dispatch_request(request, **values)
                response = self.make_response(response_data, request)
                return response
            else:
                return self.handle_error(404, "Not Found", request)
        except HTTPException as e:
            return self.handle_error(e.code, e.description, request)

    def handle_options(self, resource):
        """
        Handle an HTTP OPTIONS request for a resource.

        :param resource: The resource to handle OPTIONS for.
        :return: The HTTP response.
        """
        allowed_methods = resource.get_allowed_methods()
        headers = {'Allow': ', '.join(allowed_methods)}
        return Response(status=200, headers=headers)

    def handle_error(self, code, message, request):
        """
        Handle an HTTP error and generate an error response.

        :param code: The HTTP error code.
        :param message: The error message.
        :param request: The HTTP request object.
        :return: The error response.
        """
        if code in self.error_handlers:
            handler = self.error_handlers[code]
            response_data = handler(code, message, request)
        else:
            response_data = {'error': message}
        return self.make_response(response_data, request, status=code)

    def add_error_handler(self, code, handler_func):
        """
        Add an error handler for a specific HTTP status code.

        :param code: The HTTP status code to handle.
        :param handler_func: The error handler function.
        :return: None
        """
        self.error_handlers[code] = handler_func

    def make_response(self, response_data, request, status=200, headers=None):
        """
        Create an HTTP response based on response data.

        :param response_data: The data to include in the response.
        :param request: The HTTP request object.
        :param status: The HTTP status code (default is 200).
        :param headers: Additional headers for the response (default is None).
        :return: The HTTP response.
        """
        if not headers:
            headers = {}

        content_type = self.negotiate_content_type(request)
        response = None

        if content_type == 'application/json':
            response = self.make_json_response(response_data, status, headers)
        elif content_type == 'application/xml':
            response = self.make_xml_response(response_data, status, headers)

        response.cache_control.no_cache = True  # Disable browser caching by default
        return response

    def make_json_response(self, response_data, status=None, headers=None):
        """
        Create a JSON HTTP response.

        :param response_data: The JSON data to include in the response.
        :param status: The HTTP status code (default is 200).
        :param headers: Additional headers for the response (default is None).
        :return: The JSON HTTP response.
        """
        if status is None:
            status = 200
        if headers is None:
            headers = {}

        response = Response(json.dumps(response_data), status=status, headers=headers)
        response.content_type = 'application/json'
        return response

    def make_xml_response(self, response_data, status=None, headers=None):
        """
        Create an XML HTTP response.

        :param response_data: The XML data to include in the response.
        :param status: The HTTP status code (default is 200).
        :param headers: Additional headers for the response (default is None).
        :return: The XML HTTP response.
        """
        if status is None:
            status = 200
        if headers is None:
            headers = {}

        root = ET.Element('response')
        self.build_xml_element(root, response_data)

        xml_str = ET.tostring(root, encoding='utf-8', method='xml')
        response = Response(xml_str, status=status, headers=headers)
        response.content_type = 'application/xml'
        return response

    def build_xml_element(self, parent, data):
        """
        Build an XML element from data.

        :param parent: The parent XML element.
        :param data: The data to convert to XML.
        :return: None
        """
        if isinstance(data, dict):
            for key, value in data.items():
                element = ET.SubElement(parent, key)
                self.build_xml_element(element, value)
        elif isinstance(data, list):
            for item in data:
                element = ET.SubElement(parent, 'item')
                self.build_xml_element(element, item)
        else:
            parent.text = str(data)

    def negotiate_content_type(self, request):
        """
        Negotiate the content type based on the Accept header.

        :param request: The HTTP request object.
        :return: The negotiated content type.
        """
        accepted_types = request.headers.get('Accept', '').split(',')
        for accepted_type in accepted_types:
            if 'application/json' in accepted_type:
                return 'application/json'
            elif 'application/xml' in accepted_type:
                return 'application/xml'
        return 'application/json'

    def handle_exception(self, e, request):
        """
        Handle an exception and generate an error response.

        :param e: The exception to handle.
        :param request: The HTTP request object.
        :return: The error response.
        """
        response_data = {'error': str(e)}
        return self.make_response(response_data, request, status=getattr(e, 'code', 500))

    def wsgi_app(self, environ, start_response):
        """
        The WSGI application entry point.

        :param environ: The WSGI environment.
        :param start_response: The WSGI start_response function.
        :return: The HTTP response.
        """
        request = Request(environ)
        try:
            response = self.dispatch_request(request)
        except HTTPException as e:
            response = self.handle_exception(e, request)
        return response(environ, start_response)

    def run(self, host='localhost', port=3000, debug=False):
        """
        Run the RESTful API server.

        :param host: The host IP address (default is 'localhost').
        :param port: The port number (default is 3000).
        :param debug: Enable debugging mode (default is False).
        :return: None
        """
        self.debug = debug
        if debug:
            app = DispatcherMiddleware(self.wsgi_app, {'/__debug__': ProfilerMiddleware(self.wsgi_app)})
            from werkzeug.debug import DebuggedApplication
            app = DebuggedApplication(app, evalex=True)
        else:
            app = self.wsgi_app
        from werkzeug.serving import run_simple
        run_simple(host, port, app, use_reloader=debug)

    def __call__(self, environ, start_response):
        """
        Allow the API instance to be called as a WSGI application.

        :param environ: The WSGI environment.
        :param start_response: The WSGI start_response function.
        :return: The HTTP response.
        """
        return self.wsgi_app(environ, start_response)


class Resource:
    def __init__(self, app):
        """
        Initialize a resource for the RESTful API.

        :param app: The Restful app instance.
        :return: None
        """
        self.app = app
        self.parser = RequestParser()

    @staticmethod
    def paginate(items, page, per_page):
        """
        Paginate a list of items.

        :param items: The list of items to paginate.
        :param page: The current page number (1-indexed).
        :param per_page: The number of items per page.
        :return: A tuple containing paginated items and pagination information.
        """
        pagination = Pagination(items, page, per_page)
        paginated_items, pagination_info = pagination.paginate()
        return paginated_items, pagination_info
    
    def JsonResponse(data, status_code=200, headers=None):
        """
        Create a JSON response.

        :param data: The JSON data to be included in the response.
        :param status_code: The HTTP status code (default is 200).
        :param headers: Additional headers to include in the response (default is None).
        :return: A JSON response.
        """
        if headers is None:
            headers = {}
        
        response = Response(json.dumps(data), status=status_code, headers=headers)
        response.content_type = 'application/json'
        return response

    def XmlResponse(data, status_code=200, headers=None):
        """
        Create an XML response.

        :param data: The XML data to be included in the response.
        :param status_code: The HTTP status code (default is 200).
        :param headers: Additional headers to include in the response (default is None).
        :return: An XML response.
        """
        if headers is None:
            headers = {}
        
        response = Response(data, status=status_code, headers=headers)
        response.content_type = 'application/xml'
        return response

    def HtmlResponse(data, status_code=200, headers=None):
        """
        Create an HTML response.

        :param data: The HTML content to be included in the response.
        :param status_code: The HTTP status code (default is 200).
        :param headers: Additional headers to include in the response (default is None).
        :return: An HTML response.
        """
        if headers is None:
            headers = {}
        
        response = Response(data, status=status_code, headers=headers)
        response.content_type = 'text/html'
        return response

    def json_response(self, data, status_code=200, headers=None):
        """
        Create a JSON HTTP response.

        :param data: The JSON data to include in the response.
        :param status_code: The HTTP status code (default is 200).
        :param headers: Additional headers for the response (default is None).
        :return: The JSON HTTP response.
        """
        return self.app.make_json_response(data, status_code, headers)

    def xml_response(self, data, status_code=200, headers=None):
        """
        Create an XML HTTP response.

        :param data: The XML data to include in the response.
        :param status_code: The HTTP status code (default is 200).
        :param headers: Additional headers for the response (default is None).
        :return: The XML HTTP response.
        """
        return self.app.make_xml_response(data, status_code, headers)

    def process_input(self, request, fields):
        """
        Process and validate JSON input data.

        :param request: The HTTP request object.
        :param fields: The field configuration for input validation.
        :return: Processed input data.
        :raises: BadRequest if input is invalid.
        """
        json_data = request.get_json()
        if json_data is None:
            raise BadRequest("Invalid JSON input")

        try:
            processed_data = fields.process(json_data)
        except BadRequest as e:
            raise e

        return processed_data

    def dispatch_request(self, request, **kwargs):
        """
        Dispatch an HTTP request to the appropriate resource method.

        :param request: The HTTP request object.
        :param kwargs: Additional keyword arguments.
        :return: The HTTP response.
        :raises: MethodNotAllowed if the HTTP method is not allowed.
        """
        method = request.method.lower()
        handler = getattr(self, method, None)
        if handler:
            return handler(request, **kwargs)
        raise MethodNotAllowed(valid_methods=self.get_allowed_methods())

    def validate_input(self, request, required_fields):
        """
        Validate JSON input data against required fields.

        :param request: The HTTP request object.
        :param required_fields: List of required field names.
        :return: Validated input data.
        :raises: BadRequest if input is invalid.
        """
        json_data = request.get_json()
        if json_data is None:
            raise BadRequest("Invalid JSON input")

        missing_fields = [field for field in required_fields if field not in json_data]
        if missing_fields:
            raise BadRequest(f"Missing required fields: {', '.join(missing_fields)}")

        return json_data

    def get_allowed_methods(self):
        """
        Get a list of HTTP methods allowed for the resource.

        :return: List of allowed HTTP methods.
        """
        allowed_methods = []
        for method in dir(self):
            if method.upper() in ['GET', 'POST', 'PUT', 'DELETE']:
                allowed_methods.append(method.upper())
        return allowed_methods

    def add_route(self, rule, endpoint=None, **options):
        """
        Add a route for the resource.

        :param rule: The route URL for the resource.
        :param endpoint: The endpoint name for the resource (default is None).
        :param options: Additional route options.
        :return: None
        """
        if endpoint is None:
            endpoint = self.__class__.__name__.lower()
        self.app.route(rule, endpoint=endpoint, **options)(self)

    def set_error_handler(self, code, handler_func):
        """
        Set an error handler for a specific HTTP status code.

        :param code: The HTTP status code to handle.
        :param handler_func: The error handler function.
        :return: None
        """
        self.app.add_error_handler(code, handler_func)

    def add_namespace(self, namespace):
        """
        Add a namespace to the resource.

        :param namespace: The namespace for the resource.
        :return: None
        """
        self.app.add_namespace(namespace)

    def marshal(self, data, fields):
        """
        Marshal data using specified fields.

        :param data: The data to marshal.
        :param fields: Dictionary of fields to include.
        :return: Marshaled data.
        """
        return {field: data[field] for field in fields}

    def output(self, data, code, headers=None):
        """
        Create an HTTP response for the output data.

        :param data: The data to include in the response.
        :param code: The HTTP status code.
        :param headers: Additional headers for the response (default is None).
        :return: The HTTP response.
        """
        return self.app.make_response(data, code, headers)

    def json_response(self, data, status_code=200, headers=None):
        """
        Create a JSON HTTP response.

        :param data: The JSON data to include in the response.
        :param status_code: The HTTP status code (default is 200).
        :param headers: Additional headers for the response (default is None).
        :return: The JSON HTTP response.
        """
        return self.app.make_json_response(data, status_code, headers)

    def use_args(self, **kwargs):
        """
        Decorator to define request parser arguments for resource methods.

        :param kwargs: Request parser arguments.
        :return: Decorator function.
        """
        def decorator(func):
            request_parser = self.parser
            for name, config in kwargs.items():
                request_parser.add_argument(name, **config)

            @self.app.use_args(request_parser)
            def wrapped_func(request, args, **kwargs):
                return func(request, args, **kwargs)

            return wrapped_func

        return decorator

    def use_kwargs(self, **kwargs):
        """
        Decorator to define request parser arguments for resource methods.

        :param kwargs: Request parser arguments.
        :return: Decorator function.
        """
        def decorator(func):
            request_parser = self.parser
            for name, config in kwargs.items():
                request_parser.add_argument(name, **config)

            @self.app.use_kwargs(request_parser)
            def wrapped_func(request, **kwargs):
                return func(request, **kwargs)

            return wrapped_func


class Pagination:
    def __init__(self, items, page, per_page, total_count=None, sort_field=None, sort_order='asc', filters=None):
        """
        Initialize a Pagination instance.

        :param items: A list or query result set to paginate.
        :param page: The current page number (1-indexed).
        :param per_page: The number of items per page.
        :param total_count: The total count of items (optional).
        :param sort_field: The field to sort items by (optional).
        :param sort_order: The sort order ('asc' for ascending, 'desc' for descending).
        :param filters: A dictionary of filters to apply (e.g., {'field': 'value'}).
        """
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total_count = total_count if total_count is not None else len(items)
        self.sort_field = sort_field
        self.sort_order = sort_order
        self.filters = filters or {}

    def paginate(self):
        """
        Perform pagination on the provided items.

        :return: A dictionary containing the paginated items, pagination information, and optional links.
        """
        filtered_items = self._apply_filters(self.items, self.filters)

        if self.sort_field:
            filtered_items = self._sort_items(filtered_items, self.sort_field, self.sort_order)

        total_items = len(filtered_items)
        start_idx = (self.page - 1) * self.per_page
        end_idx = start_idx + self.per_page
        paginated_items = filtered_items[start_idx:end_idx]

        pagination_info = {
            'page': self.page,
            'per_page': self.per_page,
            'total_items': self.total_count,
            'total_pages': (self.total_count + self.per_page - 1) // self.per_page,
        }

        links = self._generate_links()

        response_data = {
            'items': paginated_items,
            'pagination': pagination_info,
            'links': links,
        }

        return response_data

    def _apply_filters(self, items, filters):
        filtered_items = items
        for field, value in filters.items():
            filtered_items = [item for item in filtered_items if item.get(field) == value]
        return filtered_items

    def _sort_items(self, items, sort_field, sort_order):
        reverse = sort_order.lower() == 'desc'
        return sorted(items, key=lambda x: x.get(sort_field), reverse=reverse)

    def _generate_links(self):
        links = {}
        if self.page > 1:
            links['prev'] = self._generate_page_link(self.page - 1)
        if self.page < self._calculate_total_pages():
            links['next'] = self._generate_page_link(self.page + 1)
        return links

    def _generate_page_link(self, page):
        # You can customize the URL format for page links here
        return f"?page={page}&per_page={self.per_page}"

    def _calculate_total_pages(self):
        return (self.total_count + self.per_page - 1) // self.per_page
    
class Field:
    def __init__(self, required=False, default=None, validate=None, choices=None):
        """
        Initialize a field for request argument processing.

        :param required: Whether the field is required (default is False).
        :param default: The default value for the field (default is None).
        :param validate: A validation function for the field (default is None).
        :param choices: A list of allowed choices for the field (default is None).
        """
        self.required = required
        self.default = default
        self.validate = validate  # A validation function
        self.choices = choices 

    def serialize(self, name, data):
        if name not in data:
            if self.required:
                raise ValueError(f"Missing required field: {name}")
            return self.default

        value = data[name]
        if self.choices and value not in self.choices:
            raise ValueError(f"Invalid choice for field {name}: {value}")

        if self.validate and not self.validate(value):
            raise ValueError(f"Validation failed for field {name}")

        return self._serialize(value)

    def deserialize(self, name, data):
        if name not in data:
            if self.required:
                raise ValueError(f"Missing required field: {name}")
            return self.default

        value = data[name]
        if self.choices and value not in self.choices:
            raise ValueError(f"Invalid choice for field {name}: {value}")

        if self.validate and not self.validate(value):
            raise ValueError(f"Validation failed for field {name}")

        return self._deserialize(value)

    def validate_email(self, email):
        import re
        email_regex = r'^[\w\.-]+@[\w\.-]+$'
        return re.match(email_regex, email) is not None

    def validate_age(self, age):
        return isinstance(age, int) and 0 <= age <= 120

class Marshal:
    def __init__(self):
        """
        Initialize a Marshal instance to facilitate data marshaling and unmarshaling.
        """
        self.fields = {}

    def add_field(self, name, field):
        """
        Add a field to the Marshal instance.

        :param name: The name of the field.
        :param field: The field configuration.
        :return: None
        """
        self.fields[name] = field

    def marshal(self, data, fields=None):
        """
        Marshal data using specified fields.

        :param data: The data to marshal.
        :param fields: Dictionary of fields to include (default is None, uses all fields).
        :return: Marshaled data.
        :raises: MarshalError if marshaling fails.
        """
        if fields is None:
            fields = self.fields

        result = {}
        errors = {}
        for name, field in fields.items():
            try:
                result[name] = field.serialize(name, data)
            except ValueError as e:
                errors[name] = str(e)

        if errors:
            raise MarshalError(errors)

        return result

    def unmarshal(self, data, fields=None):
        """
        Unmarshal data using specified fields.

        :param data: The data to unmarshal.
        :param fields: Dictionary of fields to include (default is None, uses all fields).
        :return: Unmarshaled data.
        :raises: UnmarshalError if unmarshaling fails.
        """
        if fields is None:
            fields = self.fields

        result = {}
        errors = {}
        for name, field in fields.items():
            try:
                result[name] = field.deserialize(name, data)
            except ValueError as e:
                errors[name] = str(e)

        if errors:
            raise UnmarshalError(errors)

        return result

class MarshalError(Exception):
    def __init__(self, errors):
        """
        Initialize a MarshalError exception.

        :param errors: A dictionary of errors encountered during marshaling.
        """
        self.errors = errors

class UnmarshalError(Exception):
    def __init__(self, errors):
        """
        Initialize an UnmarshalError exception.

        :param errors: A dictionary of errors encountered during unmarshaling.
        """
        self.errors = errors

class ApiError(Exception):
    def __init__(self, message, status_code=400, additional_data=None):
        """
        Initialize an ApiError exception.

        :param message: The error message.
        :param status_code: The HTTP status code (default is 400).
        :param additional_data: Additional data related to the error (default is None).
        """
        self.message = message
        self.status_code = status_code
        self.additional_data = additional_data or {}
        super().__init__(self.message)

