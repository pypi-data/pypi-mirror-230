class Middleware:
    def __init__(self, app, config=None):
        """
        Initialize a Middleware instance.

        :param app: The Restful application instance.
        :param config: Optional configuration parameters for the middleware.
        """
        self.app = app
        self.config = config or {}

    def __call__(self, resource_class):
        """
        Apply the middleware to a resource class.

        :param resource_class: The resource class to which the middleware should be applied.
        :return: A modified resource class with the middleware applied.
        """
        return self.apply_middleware(resource_class)

    def apply_middleware(self, resource_class):
        """
        Apply the middleware to a resource class.

        :param resource_class: The resource class to which the middleware should be applied.
        :return: A modified resource class with the middleware applied.
        """
        original_dispatch_request = resource_class.dispatch_request

        def wrapped_dispatch_request(request, **kwargs):
            # Middleware logic before the resource is invoked
            # For example, authentication, logging, request modification, etc.
            self.before_request(request)

            try:
                # Call the original dispatch_request method
                response = original_dispatch_request(request, **kwargs)
            except Exception as e:
                # Handle exceptions raised during resource execution
                response = self.handle_exception(e)

            # Middleware logic after the resource is invoked
            # For example, response modification, additional headers, etc.
            self.after_request(response)

            return response

        # Replace the dispatch_request method with the wrapped version
        resource_class.dispatch_request = wrapped_dispatch_request

        return resource_class

    def before_request(self, request):
        """
        Execute middleware logic before the resource is invoked.

        :param request: The request object.
        """
        pass  # Implement your middleware logic here

    def after_request(self, response):
        """
        Execute middleware logic after the resource is invoked.

        :param response: The response object.
        """
        pass  # Implement your middleware logic here

    def handle_exception(self, exception):
        """
        Handle exceptions raised during resource execution.

        :param exception: The exception object.
        :return: A response object or None (to propagate the exception).
        """
        pass  # Implement error handling logic here
