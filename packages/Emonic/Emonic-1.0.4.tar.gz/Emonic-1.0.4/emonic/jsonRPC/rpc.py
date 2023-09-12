import json
from werkzeug.wrappers import Request, Response

class JSONRPC:
    def __init__(self, app):
        self.app = app
        self.methods = {}

    def add_method(self, name, func, params_validator=None):
        self.methods[name] = {'func': func, 'params_validator': params_validator}

    def handle_jsonrpc_request(self, request):
        try:
            data = json.loads(request.data)

            if isinstance(data, list):
                responses = [self._handle_single_jsonrpc_request(req) for req in data]
            else:
                responses = [self._handle_single_jsonrpc_request(data)]

            response_data = responses if len(responses) > 1 else responses[0]

            response = Response(json.dumps(response_data), content_type='application/json')
            return response
        except Exception as e:
            error_response = self._create_error_response(None, -32603, 'Internal error', str(e))
            response = Response(json.dumps(error_response), content_type='application/json')
            return response

    def _handle_single_jsonrpc_request(self, data):
        rpc_id = data.get('id')

        if 'method' not in data:
            return self._create_error_response(rpc_id, -32600, 'Invalid request', 'Method missing')

        method = data['method']
        params = data.get('params', [])

        if method in self.methods:
            method_info = self.methods[method]
            params_validator = method_info.get('params_validator')
            if params_validator and not params_validator(*params):
                response_data = self._create_error_response(rpc_id, -32602, 'Invalid params')
            else:
                if 'id' in data:
                    try:
                        result = method_info['func'](*params)
                        response_data = self._create_success_response(rpc_id, result)
                    except CustomException as ce:
                        response_data = self._create_error_response(rpc_id, ce.code, ce.message)
                    except Exception as e:
                        response_data = self._create_error_response(rpc_id, -32000, 'Server error', str(e))
                else:
                    try:
                        method_info['func'](*params)
                        response_data = None  # For notifications, no response
                    except Exception:
                        pass
        else:
            response_data = self._create_error_response(rpc_id, -32601, 'Method not found')

        return response_data

    def _create_success_response(self, rpc_id, result):
        return {
            'jsonrpc': '2.0',
            'result': result,
            'id': rpc_id
        }

    def _create_error_response(self, rpc_id, code, message, data=None):
        error_response = {
            'jsonrpc': '2.0',
            'error': {
                'code': code,
                'message': message
            },
            'id': rpc_id
        }
        if data:
            error_response['error']['data'] = data
        return error_response

    def __call__(self, environ, start_response):
        request = Request(environ)
        if request.path == '/jsonrpc':
            return self.handle_jsonrpc_request(request)(environ, start_response)
        return self.app(environ, start_response)

class CustomException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message