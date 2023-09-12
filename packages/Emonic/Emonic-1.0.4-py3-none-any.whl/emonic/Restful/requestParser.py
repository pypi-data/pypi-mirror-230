from werkzeug.exceptions import BadRequest

class RequestParser:
    def __init__(self):
        self.args = {}
        self.kwargs = {}
        self.locations = {
            'json': 'get_json',
            'form': 'form',
            'args': 'args',
            'headers': 'headers',
            'cookies': 'cookies',
            'files': 'files',
        }

    def add_argument(self, name, location='json', required=False, type=None, choices=None, help=None):
        """
        Add an argument to be parsed from the request.

        :param name: The argument name.
        :param location: The location of the argument data ('json', 'form', 'args', 'headers', 'cookies', 'files').
        :param required: Whether the argument is required.
        :param type: The expected data type (e.g., int, str).
        :param choices: A list of valid choices for the argument (for enums).
        :param help: A help message for the argument.
        """
        argument = {
            'location': location,
            'required': required,
            'type': type,
            'choices': choices,
            'help': help,
        }
        if location == 'json':
            self.args[name] = argument
        else:
            self.kwargs[name] = argument

    def parse_args(self, request):
        """
        Parse arguments from the request.

        :param request: The request object.
        :return: A dictionary containing parsed arguments.
        """
        args = {}
        kwargs = {}
        for name, arg_config in self.args.items():
            value = self._parse_argument(request, name, arg_config)
            if value is not None:
                args[name] = value

        for name, arg_config in self.kwargs.items():
            value = self._parse_argument(request, name, arg_config)
            if value is not None:
                kwargs[name] = value

        return args, kwargs

    def _parse_argument(self, request, name, arg_config):
        location = arg_config['location']
        required = arg_config['required']
        type_ = arg_config['type']
        choices = arg_config['choices']
        help = arg_config['help']

        location_method = self.locations.get(location)
        if location_method is None:
            raise ValueError(f"Invalid argument location: {location}")

        data = getattr(request, location_method)()

        if data is None:
            if required:
                raise BadRequest(f"Missing required argument: {name}")
            else:
                return None

        value = data.get(name)
        if value is None:
            if required:
                raise BadRequest(f"Missing required argument: {name}")
            else:
                return None

        if type_ is not None:
            try:
                value = type_(value)
            except (ValueError, TypeError):
                raise BadRequest(f"Invalid value for argument '{name}'. Expected type: {type_}")

        if choices is not None and value not in choices:
            raise BadRequest(f"Invalid value for argument '{name}'. Allowed choices: {choices}")

        return value

class Namespace:
    def __init__(self, app, name, description=None, prefix=None, middleware=None, errors=None):
        """
        Initialize a new namespace.

        :param app: The Restful application instance.
        :param name: The namespace name.
        :param description: An optional description for the namespace.
        :param prefix: An optional prefix to add to all resources within the namespace.
        :param middleware: A list of middleware functions to apply to resources in the namespace.
        :param errors: A dictionary of custom error handlers for the namespace.
        """
        self.app = app
        self.name = name
        self.description = description
        self.prefix = prefix or ''
        self.middleware = middleware or []
        self.errors = errors or {}
        self.resources = []

    def add_resource(self, resource_class, route, endpoint=None, **kwargs):
        """
        Add a resource to the namespace.

        :param resource_class: The resource class to add.
        :param route: The route for the resource.
        :param endpoint: The endpoint name (defaults to the resource class name in lowercase).
        :param kwargs: Additional keyword arguments to pass when creating the resource.
        """
        if endpoint is None:
            endpoint = resource_class.__name__.lower()
        self.app.add_resource(resource_class, self.prefix + route, endpoint=endpoint, **kwargs)
        self.resources.append((self.prefix + route, endpoint))

    def set_error_handler(self, code, handler_func):
        """
        Set a custom error handler for the namespace.

        :param code: The HTTP status code to handle.
        :param handler_func: The error handler function.
        """
        self.errors[code] = handler_func

    def add_namespace(self, namespace):
        """
        Add a nested namespace to the current namespace.

        :param namespace: The nested namespace to add.
        """
        for route, endpoint in namespace.resources:
            self.resources.append((self.prefix + route, endpoint))
            self.app.resources[endpoint] = self.app.resources[namespace.name].__class__(self.app)

        for code, handler_func in namespace.errors.items():
            self.errors[code] = handler_func

    def apply_middleware(self, resource_class):
        """
        Apply middleware to a resource within the namespace.

        :param resource_class: The resource class to apply middleware to.
        """
        for middleware_func in self.middleware:
            resource_class = middleware_func(resource_class)
        return resource_class

class Arguments:
    def __init__(self):
        self.args = []
        self.groups = {}
        self.validators = {}

    def add_argument(self, name, location='json', required=False, type=None, choices=None, default=None, help=None):
        """
        Add an argument to be parsed from the request.

        :param name: The argument name.
        :param location: The location of the argument data ('json', 'form', 'args', 'headers', 'cookies', 'files').
        :param required: Whether the argument is required.
        :param type: The expected data type (e.g., int, str).
        :param choices: A list of valid choices for the argument (for enums).
        :param default: The default value for the argument.
        :param help: A help message for the argument.
        """
        argument = {
            'name': name,
            'location': location,
            'required': required,
            'type': type,
            'choices': choices,
            'default': default,
            'help': help,
        }
        self.args.append(argument)

    def add_argument_group(self, group_name, group_args):
        """
        Add a group of related arguments.

        :param group_name: The name of the argument group.
        :param group_args: A list of argument names to include in the group.
        """
        self.groups[group_name] = group_args

    def add_argument_validator(self, name, validator_func):
        """
        Add a custom validation function for an argument.

        :param name: The name of the argument to validate.
        :param validator_func: A validation function that raises an exception if invalid.
        """
        self.validators[name] = validator_func

    def parse(self, request):
        """
        Parse arguments from the request.

        :param request: The request object.
        :return: A dictionary containing parsed arguments.
        """
        args = {}
        for arg_config in self.args:
            name = arg_config['name']
            value = self._parse_argument(request, name, arg_config)
            if value is not None:
                args[name] = value
        return args

    def _parse_argument(self, request, name, arg_config):
        location = arg_config['location']
        required = arg_config['required']
        type_ = arg_config['type']
        choices = arg_config['choices']
        default = arg_config['default']
        help = arg_config['help']

        location_method = self._get_location_method(location)
        if location_method is None:
            raise ValueError(f"Invalid argument location: {location}")

        data = location_method(request)

        if data is None:
            if required:
                raise BadRequest(f"Missing required argument: {name}")
            else:
                return default

        value = data.get(name, default)
        if value is None:
            if required:
                raise BadRequest(f"Missing required argument: {name}")
            else:
                return default

        if type_ is not None:
            try:
                value = type_(value)
            except (ValueError, TypeError):
                raise BadRequest(f"Invalid value for argument '{name}'. Expected type: {type_}")

        if choices is not None and value not in choices:
            raise BadRequest(f"Invalid value for argument '{name}'. Allowed choices: {choices}")

        if name in self.validators:
            validator_func = self.validators[name]
            validation_result = validator_func(value)
            if validation_result is not None:
                raise BadRequest(f"Validation error for argument '{name}': {validation_result}")

        return value

    def _get_location_method(self, location):
        methods = {
            'json': lambda req: req.get_json(),
            'form': lambda req: req.form,
            'args': lambda req: req.args,
            'headers': lambda req: req.headers,
            'cookies': lambda req: req.cookies,
            'files': lambda req: req.files,
        }
        return methods.get(location)