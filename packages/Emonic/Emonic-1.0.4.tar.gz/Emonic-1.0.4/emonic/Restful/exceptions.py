class ErrorHandlers:
    @staticmethod
    def handle_400(code, message, request):
        """
        Handle a 400 Bad Request error.

        :param code: The error code (400).
        :param message: The error message.
        :param request: The request object.
        :return: A tuple containing the error response dictionary and status code.
        """
        return {'error': message}, code

    @staticmethod
    def handle_401(code, message, request):
        """
        Handle a 401 Unauthorized error.

        :param code: The error code (401).
        :param message: The error message.
        :param request: The request object.
        :return: A tuple containing the error response dictionary and status code.
        """
        return {'error': message}, code

    @staticmethod
    def handle_403(code, message, request):
        """
        Handle a 403 Forbidden error.

        :param code: The error code (403).
        :param message: The error message.
        :param request: The request object.
        :return: A tuple containing the error response dictionary and status code.
        """
        return {'error': message}, code

    @staticmethod
    def handle_404(code, message, request):
        """
        Handle a 404 Not Found error.

        :param code: The error code (404).
        :param message: The error message.
        :param request: The request object.
        :return: A tuple containing the error response dictionary and status code.
        """
        return {'error': message}, code

    @staticmethod
    def handle_405(code, message, request):
        """
        Handle a 405 Method Not Allowed error.

        :param code: The error code (405).
        :param message: The error message.
        :param request: The request object.
        :return: A tuple containing the error response dictionary and status code.
        """
        return {'error': message}, code

    @staticmethod
    def handle_500(code, message, request):
        """
        Handle a 500 Internal Server Error.

        :param code: The error code (500).
        :param message: The error message.
        :param request: The request object.
        :return: A tuple containing the error response dictionary and status code.
        """
        return {'error': message}, code

    @staticmethod
    def handle_503(code, message, request):
        """
        Handle a 503 Service Unavailable error.

        :param code: The error code (503).
        :param message: The error message.
        :param request: The request object.
        :return: A tuple containing the error response dictionary and status code.
        """
        return {'error': message}, code