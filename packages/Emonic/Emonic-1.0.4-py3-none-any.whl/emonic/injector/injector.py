from werkzeug.wrappers import Request, Response

class Injector:
    def __init__(self, app):
        self.app = app
        self.injected_dependencies = {}
        self.singleton_instances = {}
        self.global_dependencies = {}
        self.before_request_funcs = []
        self.after_request_funcs = []
        self.middlewares = []
        self.error_handlers = {}

    def inject(self, dependency, name=None, scope='singleton', config=None):
        def decorator(view_func):
            self.injected_dependencies[view_func] = (dependency, name, scope, config)
            return view_func
        return decorator

    def before_request(self, view_func):
        def wrapper(request, **values):
            dependency, name, scope, config = self.injected_dependencies.get(view_func, (None, None, None, None))
            if dependency:
                instance = None
                if scope == 'singleton':
                    instance = self.singleton_instances.get(name)
                if instance is None:
                    instance = dependency(**(config or {}))
                    if scope == 'singleton':
                        self.singleton_instances[name] = instance
                setattr(request, name or dependency.__name__, instance)
            return view_func(request, **values)
        self.app.before_request(wrapper)
        return view_func

    def inject_request(self, name=None, config=None):
        def decorator(dependency):
            return self.inject(dependency, name, 'request', config)
        return decorator

    def inject_singleton(self, name=None, config=None):
        def decorator(dependency):
            return self.inject(dependency, name, 'singleton', config)
        return decorator

    def inject_global(self, name=None, config=None):
        def decorator(dependency):
            self.global_dependencies[name or dependency.__name__] = (dependency, config)
            return dependency
        return decorator

    def before_request_request(self, name=None, config=None):
        def decorator(dependency):
            return self.before_request(self.inject_request(name, config)(dependency))
        return decorator

    def before_request_singleton(self, name=None, config=None):
        def decorator(dependency):
            return self.before_request(self.inject_singleton(name, config)(dependency))
        return decorator

    def before_request_global(self, name=None, config=None):
        def decorator(dependency):
            return self.before_request(self.inject_global(name, config)(dependency))
        return decorator

    def inject_param(self, param_name, name=None, config=None):
        def decorator(dependency):
            def wrapper(request, **values):
                param_value = values.get(param_name)
                if param_value is None:
                    raise ValueError(f"Missing parameter: {param_name}")
                try:
                    instance = dependency(param_value, **(config or {}))
                except Exception as e:
                    return self.handle_error(request, e)
                setattr(request, name or dependency.__name__, instance)
                return dependency(request, **values)  # Call the dependency function
            return wrapper
        return decorator

    def before_request_param(self, param_name, name=None, config=None):
        def decorator(dependency):
            return self.before_request(self.inject_param(param_name, name, config)(dependency))
        return decorator

    def process_global_dependencies(self):
        for name, (dependency, config) in self.global_dependencies.items():
            instance = dependency(**(config or {}))
            setattr(self.app, name, instance)

    def after_request_global(self, view_func):
        def wrapper(request, response):
            for name, (dependency, config) in self.global_dependencies.items():
                if hasattr(self.app, name):
                    delattr(self.app, name)  # Clean up global attributes
            return response
        self.app.after_request(wrapper)
        return view_func
    
    def handle_error(self, code, error, request):
        handler = self.error_handlers.get(code)
        if handler:
            return handler(error, request)
        else:
            return self.default_error_handler(error, request)

    def default_error_handler(self, error, request):
        response_content = f"An error occurred: {error}"
        return Response(response_content, content_type='text/plain', status=500)

    def before_request_func(self, func):
        self.before_request_funcs.append(func)
        return func

    def after_request_func(self, func):
        self.after_request_funcs.append(func)
        return func

    def preprocess_request(self, request):
        for func in self.before_request_funcs:
            response = func(request)
            if response:
                return response

    def postprocess_request(self, request, response):
        for func in self.after_request_funcs:
            response = func(request, response)
        return response
    
    def errorhandler(self, code):
        def decorator(handler):
            self.error_handlers[code] = handler
            return handler
        return decorator

    def use(self, middleware):
        self.middlewares.append(middleware)
    
    def handle_error(self, request, error):
        # Handle different types of errors here
        if isinstance(error, ValueError):
            response_content = f"Value Error: {error}"
            return Response(response_content, content_type='text/plain', status=400)
        elif isinstance(error, Exception):
            response_content = f"An error occurred: {error}"
            return Response(response_content, content_type='text/plain', status=500)

    def wsgi_app(self, environ, start_response):
        try:
            request = Request(environ)
            response = self.preprocess_request(request)
            if response:
                return response(environ, start_response)
            response = self.handle_request(request)
            response = self.postprocess_request(request, response)
        except Exception as e:
            response = self.handle_error(request, e)
        return response(environ, start_response)
