import http.client
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urlencode
import platform
import logging
import random
import zlib
import gzip
from typing import Optional, Union, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import time
import hashlib
import base64
from .sessions import Session

class HttpException(Exception):
    def __init__(self, status_code, reason, response_text, headers=None):
        """
        Initialize an HTTP exception.

        Args:
            status_code (int): The HTTP status code.
            reason (str): The reason phrase.
            response_text (str): The response text.
            headers (dict, optional): The response headers.

        Usage:
            raise HttpException(404, "Not Found", "The resource was not found.")
        """
        self.status_code = status_code
        self.reason = reason
        self.response_text = response_text
        self.headers = headers
        super().__init__(f"HTTP {status_code} - {reason}")

    def __str__(self):
        error_message = f"HTTP {self.status_code} - {self.reason}\n"
        if self.headers:
            for key, value in self.headers.items():
                error_message += f"{key}: {value}\n"
        error_message += self.response_text
        return error_message

class ApiRequest:
    def __init__(self):
        """
        Initialize the ApiRequest manager.

        Usage:
            api_request = ApiRequest()
        """
        self.default_timeout = 10  # Default timeout in seconds
        self.max_redirects = 5
        self.session = None
        self.connection_pool = {}
        self.user_agents = self._get_user_agent()
        self.logger = self._configure_logger()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.request_retries = 3  # Number of times to retry a request on failure
        self.cache = {}
        self.response_cache_max_size = 1000
        self.default_headers = {}  # Default headers for requests
        self.proxy = None  # Proxy configuration
        self.use_response_cache = True

    def _get_user_agent(self):
        user_agent = f"Python/{platform.python_version()} ({platform.system()}; {platform.release()})"
        return [user_agent]  # Store user agents as a list

    def _configure_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def set_default_timeout(self, timeout):
        """
        Set the default timeout for requests.

        Args:
            timeout (int): The default timeout in seconds.

        Usage:
            api_request.set_default_timeout(15)
        """
        self.default_timeout = timeout

    def set_max_redirects(self, max_redirects):
        """
        Set the maximum number of redirects to follow.

        Args:
            max_redirects (int): The maximum number of redirects.

        Usage:
            api_request.set_max_redirects(10)
        """
        self.max_redirects = max_redirects

    def set_request_retries(self, retries):
        """
        Set the number of times to retry a request on failure.

        Args:
            retries (int): The number of retry attempts.

        Usage:
            api_request.set_request_retries(5)
        """
        self.request_retries = retries

    def add_default_header(self, key, value):
        """
        Add a default header for requests.

        Args:
            key (str): The header key.
            value (str): The header value.

        Usage:
            api_request.add_default_header('Authorization', 'Bearer <token>')
        """
        self.default_headers[key] = value

    def remove_default_header(self, key):
        """
        Remove a default header.

        Args:
            key (str): The header key.

        Usage:
            api_request.remove_default_header('Authorization')
        """
        if key in self.default_headers:
            del self.default_headers[key]

    def set_default_headers(self, headers):
        """
        Set the default headers for requests.

        Args:
            headers (dict): A dictionary of headers.

        Usage:
            headers = {'Authorization': 'Bearer <token>'}
            api_request.set_default_headers(headers)
        """
        self.default_headers = headers

    def add_user_agent(self, user_agent):
        """
        Add a user agent to the list of user agents.

        Args:
            user_agent (str): The user agent string.

        Usage:
            api_request.add_user_agent('MyCustomUserAgent/1.0')
        """
        self.user_agents.append(user_agent)

    def remove_user_agent(self, user_agent):
        """
        Remove a user agent from the list of user agents.

        Args:
            user_agent (str): The user agent string.

        Usage:
            api_request.remove_user_agent('MyCustomUserAgent/1.0')
        """
        if user_agent in self.user_agents:
            self.user_agents.remove(user_agent)

    def set_user_agent(self, user_agent):
        """
        Set the user agent to a single user agent string.

        Args:
            user_agent (str): The user agent string.

        Usage:
            api_request.set_user_agent('MyCustomUserAgent/1.0')
        """
        self.user_agents = [user_agent]

    def set_proxy(self, proxy):
        """
        Set a proxy configuration for requests.

        Args:
            proxy (dict): A dictionary with 'host' and 'port' keys.

        Usage:
            proxy_config = {'host': 'proxy.example.com', 'port': 8080}
            api_request.set_proxy(proxy_config)
        """
        self.proxy = proxy

    def remove_proxy(self):
        """
        Remove the proxy configuration.

        Usage:
            api_request.remove_proxy()
        """
        self.proxy = None

    def clear_cache(self):
        """
        Clear the response cache.

        Usage:
            api_request.clear_cache()
        """
        self.cache.clear()

    def close_connections(self):
        """
        Close all HTTP connections in the connection pool.

        Usage:
            api_request.close_connections()
        """
        for conn in self.connection_pool.values():
            conn.close()
        self.connection_pool.clear()

    def enable_response_cache(self):
        """
        Enable response caching.

        Usage:
            api_request.enable_response_cache()
        """
        self.use_response_cache = True

    def disable_response_cache(self):
        """
        Disable response caching.

        Usage:
            api_request.disable_response_cache()
        """
        self.use_response_cache = False

    def get(self, url, headers=None, params=None, timeout=None, retries=None, use_cache=True, auth=None):
        """
        Send a GET request.

        Args:
            url (str): The URL to send the GET request to.
            headers (dict, optional): Additional headers for the request.
            params (dict, optional): URL parameters.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object.

        Usage:
            response = api_request.get('https://api.example.com/data')
        """
        return self.request("GET", url, headers=headers, params=params, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def post(self, url, headers=None, data=None, json_data=None, files=None, timeout=None, retries=None, use_cache=True, auth=None):
        """
        Send a POST request.

        Args:
            url (str): The URL to send the POST request to.
            headers (dict, optional): Additional headers for the request.
            data (str, optional): Request body data as a string.
            json_data (dict, optional): Request body data as JSON.
            files (dict, optional): Files to upload.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object.

        Usage:
            response = api_request.post('https://api.example.com/upload', data='file_data')
        """
        return self.request("POST", url, headers=headers, data=data, json_data=json_data, files=files, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def put(self, url, headers=None, data=None, json_data=None, timeout=None, retries=None, use_cache=True, auth=None):
        """
        Send a PUT request.

        Args:
            url (str): The URL to send the PUT request to.
            headers (dict, optional): Additional headers for the request.
            data (str, optional): Request body data as a string.
            json_data (dict, optional): Request body data as JSON.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object.

        Usage:
            response = api_request.put('https://api.example.com/update', data='updated_data')
        """
        return self.request("PUT", url, headers=headers, data=data, json_data=json_data, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def delete(self, url, headers=None, timeout=None, retries=None, use_cache=True, auth=None):
        """
        Send a DELETE request.

        Args:
            url (str): The URL to send the DELETE request to.
            headers (dict, optional): Additional headers for the request.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object.

        Usage:
            response = api_request.delete('https://api.example.com/resource')
        """
        return self.request("DELETE", url, headers=headers, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def head(self, url, headers=None, params=None, timeout=None, retries=None, use_cache=True, auth=None):
        """
        Send a HEAD request.

        Args:
            url (str): The URL to send the HEAD request to.
            headers (dict, optional): Additional headers for the request.
            params (dict, optional): URL parameters.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object.

        Usage:
            response = api_request.head('https://api.example.com/resource')
        """
        return self.request("HEAD", url, headers=headers, params=params, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def patch(self, url, headers=None, data=None, json_data=None, timeout=None, retries=None, use_cache=True, auth=None):
        """
        Send a PATCH request.

        Args:
            url (str): The URL to send the PATCH request to.
            headers (dict, optional): Additional headers for the request.
            data (str, optional): Request body data as a string.
            json_data (dict, optional): Request body data as JSON.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object.

        Usage:
            response = api_request.patch('https://api.example.com/patch', data='patched_data')
        """
        return self.request("PATCH", url, headers=headers, data=data, json_data=json_data, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def options(self, url, headers=None, params=None, timeout=None, retries=None, use_cache=True, auth=None):
        """
        Send an OPTIONS request.

        Args:
            url (str): The URL to send the OPTIONS request to.
            headers (dict, optional): Additional headers for the request.
            params (dict, optional): URL parameters.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object.

        Usage:
            response = api_request.options('https://api.example.com/options')
        """
        return self.request("OPTIONS", url, headers=headers, params=params, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Union[str, int]]] = None,
        data: Optional[str] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        use_cache: bool = True,
        auth: Optional[Dict[str, str]] = None
    ):
        """
        Send an HTTP request.

        Args:
            method (str): The HTTP method (GET, POST, PUT, DELETE, etc.).
            url (str): The URL to send the request to.
            headers (dict, optional): Additional headers for the request.
            params (dict, optional): URL parameters.
            data (str, optional): Request body data as a string.
            json_data (dict, optional): Request body data as JSON.
            files (dict, optional): Files to upload.
            timeout (float, optional): Request timeout in seconds.
            retries (int, optional): Number of request retries on failure.
            use_cache (bool, optional): Whether to use response caching.
            auth (dict, optional): Authentication credentials.

        Returns:
            Response: The response object or None if the request fails.

        Usage:
            response = api_request.request('GET', 'https://api.example.com/resource')
        """
        if timeout is None:
            timeout = self.default_timeout
        if retries is None:
            retries = self.request_retries

        cache_key = self._generate_cache_key(method, url, headers, params, data, json_data)
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        for _ in range(retries + 1):
            try:
                response = self._make_request(method, url, headers, params, data, json_data, files, timeout, auth)
                if response is not None:
                    if use_cache:
                        self._cache_response(cache_key, response)
                    return response
            except HttpException as e:
                self.logger.error(f"Request error: {e}")
                time.sleep(2 ** _)  # Exponential backoff for retries
        return None

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]],
        params: Optional[Dict[str, Union[str, int]]],
        data: Optional[str],
        json_data: Optional[Dict[str, Any]],
        files: Optional[Dict[str, Any]],
        timeout: Optional[float],
        auth: Optional[Dict[str, str]]
    ):
        url_parsed = urlparse(url)
        host = url_parsed.hostname
        port = url_parsed.port or 80
        path = url_parsed.path or '/'
        query = url_parsed.query

        if params:
            query += "?" + urlencode(params)

        conn_key = f"{host}:{port}"
        if conn_key not in self.connection_pool:
            self.connection_pool[conn_key] = http.client.HTTPConnection(host, port, timeout=timeout)

        user_agent = random.choice(self.user_agents)
        headers = headers or {}
        headers["Host"] = conn_key
        headers["User-Agent"] = user_agent

        if auth:
            auth_header = self._generate_auth_header(auth)
            headers.update(auth_header)

        conn = self.connection_pool[conn_key]
        body = None
        if json_data:
            data = json.dumps(json_data)
            headers["Content-Type"] = "application/json"
            body = data.encode()

        if data:
            headers["Content-Length"] = str(len(data))
            body = data.encode()

        try:
            if self.proxy:
                conn.set_tunnel(host, port, headers={'Host': url})
                conn.connect(self.proxy['host'], self.proxy['port'])
            else:
                conn.request(method, path + '?' + query, body=body, headers=headers)
            response = conn.getresponse()

            response_text = self._decode_response(response)

            if response.status >= 400:
                raise HttpException(response.status, response.reason, response_text, response.headers)

            content_type = response.headers.get("Content-Type", "")
            response_obj = Response(response.status, response_text, response.headers, content_type)
            return response_obj
        except HttpException:
            raise  # Re-raise HttpException for retries
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            return None
        finally:
            conn.close()

    def create_session(self):
        if self.session is None:
            self.session = Session(self)
        return self.session

    def _decode_response(self, response):
        content_encoding = response.headers.get('Content-Encoding', '')
        if 'gzip' in content_encoding:
            return gzip.decompress(response.read()).decode()
        elif 'deflate' in content_encoding:
            return zlib.decompress(response.read(), -zlib.MAX_WBITS).decode()
        else:
            return response.read().decode()

    def _generate_cache_key(self, method, url, headers, params, data, json_data):
        cache_key = hashlib.sha1()
        cache_key.update(method.encode())
        cache_key.update(url.encode())
        cache_key.update(json.dumps(headers).encode())
        cache_key.update(json.dumps(params).encode() if params else b'')
        cache_key.update(data.encode() if data else b'')
        cache_key.update(json.dumps(json_data).encode() if json_data else b'')
        return cache_key.hexdigest()

    def _cache_response(self, cache_key, response):
        if len(self.cache) >= self.response_cache_max_size:
            self.cache.popitem(last=False)  # Remove the oldest item
        self.cache[cache_key] = response

    def _generate_auth_header(self, auth):
        if auth['type'] == 'basic':
            user_pass = f"{auth['username']}:{auth['password']}"
            basic_auth = base64.b64encode(user_pass.encode()).decode()
            return {"Authorization": f"Basic {basic_auth}"}

class Response:
    def __init__(self, status_code: int, text: str, headers: dict, content_type: str):
        """
        Initialize an HTTP response.

        Args:
            status_code (int): The HTTP status code.
            text (str): The response text.
            headers (dict): The response headers.
            content_type (str): The content type of the response.

        Usage:
            response = Response(200, 'OK', {'Content-Type': 'text/plain'}, 'text/plain')
        """
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.content_type = content_type
    
    def json(self) -> dict:
        """
        Get the JSON content of the response.

        Returns:
            dict: The JSON data or None if parsing fails.

        Usage:
            data = response.json()
        """
        try:
            return json.loads(self.text)
        except json.JSONDecodeError:
            return None

    def xml(self):
        """
        Parse the response as XML.

        Returns:
            ElementTree.Element: The root element of the XML or None if parsing fails.

        Usage:
            xml_root = response.xml()
        """
        if "application/xml" in self.content_type:
            return ET.fromstring(self.text)
        return None

    def text(self):
        """
        Get the text content of the response.

        Returns:
            str: The response text.

        Usage:
            text = response.text()
        """
        return self.text

    def headers(self):
        """
        Get the response headers.

        Returns:
            dict: The response headers.

        Usage:
            headers = response.headers()
        """
        return self.headers

    def status_code(self):
        """
        Get the HTTP status code.

        Returns:
            int: The HTTP status code.

        Usage:
            status_code = response.status_code()
        """
        return self.status_code

    def content_type(self):
        """
        Get the content type of the response.

        Returns:
            str: The content type.

        Usage:
            content_type = response.content_type()
        """
        return self.content_type

    def get_header(self, key):
        """
        Get a specific header from the response.

        Args:
            key (str): The header key.

        Returns:
            str: The header value or None if the header is not found.

        Usage:
            content_length = response.get_header('Content-Length')
        """
        return self.headers.get(key)

    def is_success(self):
        """
        Check if the response represents a successful HTTP request (status code 2xx).

        Returns:
            bool: True if the response is successful, False otherwise.

        Usage:
            success = response.is_success()
        """
        return 200 <= self.status_code < 300

    def is_redirect(self):
        """
        Check if the response represents a HTTP redirect (status code 3xx).

        Returns:
            bool: True if the response is a redirect, False otherwise.

        Usage:
            is_redirect = response.is_redirect()
        """
        return 300 <= self.status_code < 400

    def is_client_error(self):
        """
        Check if the response represents a client error (status code 4xx).

        Returns:
            bool: True if the response is a client error, False otherwise.

        Usage:
            is_client_error = response.is_client_error()
        """
        return 400 <= self.status_code < 500

    def is_server_error(self):
        """
        Check if the response represents a server error (status code 5xx).

        Returns:
            bool: True if the response is a server error, False otherwise.

        Usage:
            is_server_error = response.is_server_error()
        """
        return 500 <= self.status_code < 600

    def has_header(self, key):
        """
        Check if a specific header is present in the response.

        Args:
            key (str): The header key.

        Returns:
            bool: True if the header is present, False otherwise.

        Usage:
            has_content_type = response.has_header('Content-Type')
        """
        return key in self.headers

    def cookie(self, name):
        """
        Get the value of a specific cookie from the response.

        Args:
            name (str): The cookie name.

        Returns:
            str: The cookie value or None if the cookie is not found.

        Usage:
            session_id = response.cookie('session_id')
        """
        cookies = self.headers.get('Set-Cookie', '').split(';')
        for cookie in cookies:
            parts = cookie.strip().split('=')
            if len(parts) == 2 and parts[0] == name:
                return parts[1]
        return None

    def cookies(self):
        """
        Get all cookies from the response.

        Returns:
            dict: A dictionary of cookies (name-value pairs).

        Usage:
            all_cookies = response.cookies()
        """
        cookies = {}
        cookie_header = self.headers.get('Set-Cookie', '')
        cookie_parts = cookie_header.split(';')
        for part in cookie_parts:
            key_value = part.strip().split('=')
            if len(key_value) == 2:
                cookies[key_value[0]] = key_value[1]
        return cookies
