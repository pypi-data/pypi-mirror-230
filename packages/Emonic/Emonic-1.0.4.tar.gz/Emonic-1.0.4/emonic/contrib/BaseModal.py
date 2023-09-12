from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.utils import send_from_directory, safe_join
from ..core.branch import Emonic, Response, json, SharedDataMiddleware, Environment, FileSystemLoader, url_encode, Map, base64, os
from ..globals import csrf
from urllib.parse import urljoin, urlencode

app = Emonic(__name__)

def render(template_name, **kwargs):
    """
    Render a template with the provided context.

    Args:
        template_name (str): The name of the template file.
        **kwargs: Additional context data to pass to the template.

    Returns:
        Response: The response with the rendered template.

    Usage:
        response = render('template.html', var1='value1', var2='value2')
    """
    template = app.template_env.get_template(template_name)
    kwargs['url_for'] = url_for
    kwargs['csrf_token'] = csrf.generate_csrf_token()
    kwargs['flashes'] = get_flashes()  # Pass flashed messages to the template
    
    # Clear flashed messages after rendering
    clear_flashes()
    
    response = Response(template.render(**kwargs), mimetype='text/html')
    csrf.set_csrf_token_cookie(response, kwargs['csrf_token'])
    return response

def clear_flashes():
    """
    Clear all flashed messages.

    Usage:
        clear_flashes()
    """
    app.messages = []

def flash(message, category='message'):
    """
    Flash a message to be displayed on the next request.

    Args:
        message (str): The message to be flashed.
        category (str, optional): The category of the message (e.g., 'success', 'error', 'info').

    Usage:
        flash('This is a success message', category='success')
    """
    app.messages.append((category, message))

def get_flashes(with_categories=False, category_filter=()):
    """
    Get flashed messages.

    Args:
        with_categories (bool, optional): If True, return messages as (category, message) tuples.
        category_filter (tuple, optional): Filter messages by category.

    Returns:
        list: A list of flashed messages.

    Usage:
        messages = get_flashes(with_categories=True, category_filter=('success', 'info'))
    """
    flashes = list(app.messages)
    if not with_categories:
        return [message for _, message in flashes]
    return [message for message in flashes if not category_filter or message[0] in category_filter]

# JSON response function
def JsonResponse(data):
    """
    Create a JSON response.

    Args:
        data (dict): The JSON data to be returned in the response.

    Returns:
        Response: The JSON response.

    Usage:
        response = JsonResponse({'key': 'value'})
    """
    json_data = json.dumps(data)
    return Response(json_data, mimetype='application/json')

# Redirect function
def redirect(location, code=302) -> Response:
    """
    Create a redirect response.

    Args:
        location (str): The URL to redirect to.
        code (int, optional): The HTTP status code for the redirect (default is 302).

    Returns:
        Response: The redirect response.

    Usage:
        response = redirect('/new_location', code=301)
    """
    return Response('', status=code, headers={'Location': location})

# URL building function
def url_for(endpoint, **values) -> str:
    """
    Build a URL for a given endpoint.

    Args:
        endpoint (str): The endpoint name.
        **values: URL parameters for the endpoint.

    Returns:
        str: The generated URL.

    Usage:
        url = url_for('user_profile', username='john_doe')
    """
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            return f'/{app.static_folder}/{filename}'
        else:
            raise ValueError("Static filename not provided")

    elif endpoint == 'redirect':
        location = values.get('location', None)
        if location:
            args = values.get('args', {})
            if args:
                location = urljoin(location, f'?{urlencode(args)}')
            return location
        else:
            raise ValueError("Redirect location not provided")

    # Other endpoint cases here...

    else:
        raise ValueError("Unknown endpoint")

# Send file with headers function
def send_file(filename, mimetype):
    """
    Send a file as a response with specified headers.

    Args:
        filename (str): The path to the file to send.
        mimetype (str): The MIME type of the file.

    Returns:
        Response: The response containing the file.

    Usage:
        response = send_file('path/to/file.txt', 'text/plain')
    """
    with open(filename, 'rb') as f:
        content = f.read()
    headers = {'Content-Type': mimetype, 'Content-Disposition': f'attachment; filename={os.path.basename(filename)}'}
    return Response(content, headers=headers)

# Middleware for serving static files
def static_engine(static_folder):
    """
    Configure static file serving middleware.

    Args:
        static_folder (str): The path to the static files folder.

    Usage:
        static_engine('static_folder')
    """
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {'/static': static_folder})

# Set template loader
def template_engine(template_folder):
    """
    Configure the template engine with a template folder.

    Args:
        template_folder (str): The path to the template folder.

    Usage:
        template_engine('template_folder')
    """
    app.template_env = Environment(loader=FileSystemLoader(template_folder))

# Save JSON content to a file
def SaveJsonContent(data, filename):
    """
    Save JSON content to a file.

    Args:
        data (dict): The JSON data to be saved.
        filename (str): The path to the output file.

    Usage:
        SaveJsonContent({'key': 'value'}, 'output.json')
    """
    with open(filename, 'w') as f:
        json.dump(data, f)

# Redirect with query parameters function
def redirect_args(location, **kwargs):
    """
    Create a redirect response with query parameters.

    Args:
        location (str): The URL to redirect to.
        **kwargs: Query parameters as keyword arguments.

    Returns:
        Response: The redirect response.

    Usage:
        response = redirect_args('/new_location', param1='value1', param2='value2')
    """
    query_params = url_encode(kwargs)
    url = f'{location}?{query_params}' if kwargs else location
    return Response(status=302, headers={'Location': url})

# Map routes using rules
def url_map(rules):
    """
    Create a URL map using a list of rules.

    Args:
        rules (list): A list of URL routing rules.

    Returns:
        Map: The URL map.

    Usage:
        my_url_map = url_map([
            Rule('/page1', endpoint='page1'),
            Rule('/page2', endpoint='page2'),
        ])
    """
    return Map(rules)

# Stream with context function
def stream_with_context(generator_or_function):
    """
    Create a response from a generator or function with streaming content.

    Args:
        generator_or_function (generator or function): A generator or function that yields content.

    Returns:
        Response: The response with streaming content.

    Usage:
        def my_generator():
            yield 'Chunk 1'
            yield 'Chunk 2'
        response = stream_with_context(my_generator)
    """
    def generate():
        for item in generator_or_function():
            yield item
    return Response(generate())

# Generate a unique key
def make_unique_key():
    """
    Generate a unique key.

    Returns:
        str: The unique key.

    Usage:
        unique_key = make_unique_key()
    """
    return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('ascii')

# Encode URLs safely
def url_quote(url, safe='/', encoding=None, errors=None):
    """
    Safely encode a URL.

    Args:
        url (str): The URL to encode.
        safe (str, optional): Characters that should not be percent-encoded (default is '/').
        encoding (str, optional): The character encoding to use (default is None).
        errors (str, optional): The error handling strategy for encoding (default is None).

    Returns:
        str: The encoded URL.

    Usage:
        encoded_url = url_quote('https://example.com/my path/', safe='/')
    """
    return url_quote(url, safe=safe, encoding=encoding, errors=errors)

def url_quote_plus(url, safe='/', encoding=None, errors=None):
    """
    Safely encode a URL with '+' character replaced by ' '.

    Args:
        url (str): The URL to encode.
        safe (str, optional): Characters that should not be percent-encoded (default is '/').
        encoding (str, optional): The character encoding to use (default is None).
        errors (str, optional): The error handling strategy for encoding (default is None).

    Returns:
        str: The encoded URL.

    Usage:
        encoded_url = url_quote_plus('https://example.com/my+path/', safe='/')
    """
    return url_quote_plus(url, safe=safe, encoding=encoding, errors=errors)

# Join directory paths safely
def safe_join(directory, *pathnames):
    """
    Join directory paths safely.

    Args:
        directory (str): The base directory path.
        *pathnames: Additional path segments to join.

    Returns:
        str: The safely joined path.

    Usage:
        joined_path = safe_join('/base/dir', 'subdir', 'file.txt')
    """
    return safe_join(directory, *pathnames)

# Set context processor
def context_processor(f):
    """
    Register a context processor function.

    Args:
        f (function): The context processor function.

    Usage:
        @context_processor
        def my_context_processor():
            return {'key': 'value'}
    """
    app.template_env.globals.update(f())

# Open resource file
def open_resource(resource):
    """
    Open a resource file.

    Args:
        resource (str): The path to the resource file.

    Returns:
        File: The opened resource file.

    Usage:
        file = open_resource('path/to/resource.txt')
    """
    return open(resource, 'rb')

# Define template filters
def template_filter(name=None):
    """
    Register a template filter.

    Args:
        name (str, optional): The name of the filter (default is None).

    Returns:
        function: The decorator to register the filter.

    Usage:
        @template_filter
        def my_template_filter(value):
            return modified_value
    """
    def decorator(f):
        app.template_env.filters[name or f.__name__] = f
        return f
    return decorator

# Set URL defaults for view functions
def url_defaults(f):
    """
    Register URL defaults for a view function.

    Args:
        f (function): The view function.

    Usage:
        @url_defaults
        def my_view_function(request, **kwargs):
            return {'param1': 'value1', 'param2': 'value2'}
    """
    app.url_map.url_defaults(f)

# Get attribute from a template
def get_template_attribute(template_name, attribute):
    """
    Get an attribute from a template.

    Args:
        template_name (str): The name of the template.
        attribute (str): The name of the attribute to retrieve.

    Returns:
        Any: The value of the template attribute.

    Usage:
        attribute_value = get_template_attribute('template.html', 'my_attribute')
    """
    return getattr(app.template_env.get_template(template_name), attribute)

# Abort request with HTTPException
def abort(code):
    """
    Abort a request with an HTTP exception.

    Args:
        code (int): The HTTP status code for the exception.

    Usage:
        abort(404)
    """
    raise HTTPException(code)

# Make response with appropriate content type
def make_response(response, status=200, headers=None):
    """
    Create a response with appropriate content type.

    Args:
        response (str, bytes, or Response): The response content.
        status (int, optional): The HTTP status code (default is 200).
        headers (dict, optional): Additional response headers (default is None).

    Returns:
        Response: The response object.

    Usage:
        response = make_response('Hello, World!', status=200, headers={'Content-Type': 'text/plain'})
    """
    if isinstance(response, (str, bytes)):
        return Response(response, status=status, headers=headers)
    return response

def XmlResponse(xml_data):
    """
    Create an XML response with the provided XML data.

    Args:
        xml_data (str): The XML content to be included in the response.

    Returns:
        Response: The XML response.
    """
    response = Response(xml_data, content_type='application/xml')
    return response

def CsvResponse(data, filename=None):
    """
    Create a CSV response.

    Args:
        data (str): The CSV data as a string.
        filename (str, optional): The name of the CSV file for the response. Defaults to None.

    Returns:
        Response: The CSV response.
    """
    response = Response(data, content_type='text/csv')
    if filename:
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response

def PdfResponse(data, filename=None):
    """
    Create a PDF response.

    Args:
        data (str): The PDF data as a string.
        filename (str, optional): The name of the PDF file for the response. Defaults to None.

    Returns:
        Response: The PDF response.
    """
    response = Response(data, content_type='application/pdf')
    if filename:
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response
