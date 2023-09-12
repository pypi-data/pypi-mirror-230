from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, HTTPException
import json
import concurrent.futures
from datetime import datetime

class Multiprocessor:
    def __init__(self, app):
        self.app = app

    def execute_hooks(self, hooks, request):
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(hook, request) for hook in hooks]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        return results

    def preprocess_request(self, request):
        before_request_results = self.execute_hooks(self.app.before_request_funcs, request)
        if any(result for result in before_request_results):
            return before_request_results[0]

    def postprocess_request(self, request, response):
        after_request_results = self.execute_hooks(self.app.after_request_funcs, request)
        return response

    def handle_request(self, request):
        adapter = self.app.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            handler = getattr(self.app, endpoint)

            response = self.app.preprocess_request(request)
            if response:
                return response

            # Execute the handler using ProcessPoolExecutor for parallel processing
            with concurrent.futures.ProcessPoolExecutor() as executor:
                future = executor.submit(handler, request, **values)
                handler_response = future.result()

            response = self.app.postprocess_request(request, handler_response)

        except NotFound as e:
            response = self.app.handle_error(404, e, request)
        except HTTPException as e:
            response = e
        return response

    def __call__(self, environ, start_response):
        request = Request(environ)
        for blueprint in self.app.blueprints:
            if request.path.startswith(blueprint.url_prefix):
                request.blueprint = blueprint
                response = blueprint.wsgi_app(environ, start_response)
                return response

        session_id = request.cookies.get('session_id')
        session_data_str = self.app.session_manager.load_session(session_id)

        if session_data_str:
            session_data = json.loads(session_data_str)
        else:
            session_data = {}

        request.session = session_data

        response = self.handle_request(request)

        serialized_session = json.dumps(request.session)
        session_id = self.app.session_manager.save_session(serialized_session)
        session_expiration = datetime.now() + self.app.session_manager.session_lifetime

        if isinstance(response, Response):
            response.set_cookie('session_id', session_id['session_id'], expires=session_expiration, secure=True, httponly=True)

        return response(environ, start_response)
