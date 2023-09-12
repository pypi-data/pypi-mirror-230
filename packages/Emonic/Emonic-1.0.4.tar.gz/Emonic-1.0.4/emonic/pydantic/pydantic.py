from functools import wraps
from pydantic import ValidationError
from werkzeug.wrappers import Response
import json

class Pydantic:
    def __init__(self, app=None, data_model=None, error_messages=None):
        self.app = app
        self.data_model = data_model
        self.error_messages = error_messages or {}

    def init_app(self, app, data_model=None):
        self.app = app
        self.data_model = data_model

    def validate(self, location='json'):
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if location == 'json':
                    data = request.get_json()
                elif location == 'query':
                    data = request.args.to_dict()
                else:
                    raise ValueError("Invalid location parameter")

                try:
                    validated_data = self.data_model(**data)
                except ValidationError as e:
                    errors = e.errors()
                    for field, error_msg in self.error_messages.items():
                        if field in errors:
                            errors[field][0]['msg'] = error_msg

                    response_content = json.dumps({"error": "Validation Error", "details": errors})
                    return Response(response_content, content_type='application/json', status=400)

                return func(request, validated_data, *args, **kwargs)
            return wrapper
        return decorator

    def before_request(self, location='json'):
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if location == 'json':
                    data = request.get_json()
                elif location == 'query':
                    data = request.args.to_dict()
                else:
                    raise ValueError("Invalid location parameter")

                try:
                    validated_data = self.data_model(**data)
                except ValidationError as e:
                    errors = e.errors()
                    for field, error_msg in self.error_messages.items():
                        if field in errors:
                            errors[field][0]['msg'] = error_msg

                    response_content = json.dumps({"error": "Validation Error", "details": errors})
                    return Response(response_content, content_type='application/json', status=400)

                setattr(request, 'validated_data', validated_data)
                return func(request, *args, **kwargs)
            return wrapper
        return decorator

    def path_params(self):
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                path_params = request.view_args
                return func(request, path_params, *args, **kwargs)
            return wrapper
        return decorator

    def header(self, name):
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                header_value = request.headers.get(name)
                return func(request, header_value, *args, **kwargs)
            return wrapper
        return decorator

    def cookie(self, name):
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                cookie_value = request.cookies.get(name)
                return func(request, cookie_value, *args, **kwargs)
            return wrapper
        return decorator

    def query_param(self, param_name):
        def decorator(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                query_params = request.args.to_dict()
                query_value = query_params.get(param_name)
                return func(request, query_value, *args, **kwargs)
            return wrapper
        return decorator
