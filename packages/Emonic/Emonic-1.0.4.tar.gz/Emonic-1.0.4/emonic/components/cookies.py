from http.cookies import SimpleCookie
from ..core.branch import Emonic

app = Emonic(__name__)

class CookieManager:
    def __init__(self):
        """
        Initialize the CookieManager.

        Usage:
            cookie_manager = CookieManager()
        """
        self.cookie_jar = SimpleCookie()

    def create_cookie(self, key, value, max_age=None, expires=None, path='/', domain=None, secure=None, httponly=False, samesite=None):
        """
        Create a cookie string.

        Args:
            key (str): The name of the cookie.
            value (str): The value to set for the cookie.
            max_age (int, optional): The maximum age of the cookie in seconds.
            expires (datetime, optional): The expiration date and time for the cookie.
            path (str, optional): The path for which the cookie is valid (default is '/').
            domain (str, optional): The domain for which the cookie is valid.
            secure (bool, optional): Whether the cookie should only be sent over HTTPS.
            httponly (bool, optional): Whether the cookie should be accessible only via HTTP.
            samesite (str, optional): The SameSite attribute for the cookie ('Strict', 'Lax', or 'None').

        Returns:
            str: The cookie string.

        Usage:
            cookie_str = cookie_manager.create_cookie('my_cookie', 'cookie_value', max_age=3600)
        """
        cookie = SimpleCookie()
        cookie[key] = value
        if max_age is not None:
            cookie[key]['max-age'] = max_age
        if expires is not None:
            cookie[key]['expires'] = expires
        cookie[key]['path'] = path
        if domain is not None:
            cookie[key]['domain'] = domain
        if secure:
            cookie[key]['secure'] = secure
        if httponly:
            cookie[key]['httponly'] = True
        if samesite is not None:
            cookie[key]['samesite'] = samesite
        return cookie.output(header='').strip()

    def set_cookie(self, key, value, max_age=None, expires=None, path='/', domain=None, secure=None, httponly=False, samesite=None):
        """
        Set a cookie.

        Args:
            key (str): The name of the cookie.
            value (str): The value to set for the cookie.
            max_age (int, optional): The maximum age of the cookie in seconds.
            expires (datetime, optional): The expiration date and time for the cookie.
            path (str, optional): The path for which the cookie is valid (default is '/').
            domain (str, optional): The domain for which the cookie is valid.
            secure (bool, optional): Whether the cookie should only be sent over HTTPS.
            httponly (bool, optional): Whether the cookie should be accessible only via HTTP.
            samesite (str, optional): The SameSite attribute for the cookie ('Strict', 'Lax', or 'None').

        Usage:
            cookie_manager.set_cookie('my_cookie', 'cookie_value', max_age=3600)
        """
        cookie = self.create_cookie(key, value, max_age, expires, path, domain, secure, httponly, samesite)
        self.cookie_jar[key] = cookie

    def get_cookie(self, key, default=None):
        """
        Get the value of a cookie.

        Args:
            key (str): The name of the cookie.
            default: The default value to return if the cookie is not found.

        Returns:
            str: The value of the cookie or the default value.

        Usage:
            cookie_value = cookie_manager.get_cookie('my_cookie', 'default_value')
        """
        return self.cookie_jar.get(key, default)

    def delete_cookie(self, key, path='/', domain=None):
        """
        Delete a cookie.

        Args:
            key (str): The name of the cookie.
            path (str, optional): The path for which the cookie is valid (default is '/').
            domain (str, optional): The domain for which the cookie is valid.

        Usage:
            cookie_manager.delete_cookie('my_cookie', path='/my_path')
        """
        self.set_cookie(key, '', expires=0, path=path, domain=domain)
