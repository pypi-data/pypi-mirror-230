import hashlib
import json
import time
from functools import wraps

class EmonicCache:
    def __init__(self, cache_duration=300):
        """
        Initialize the EmonicCache.

        Args:
            cache_duration (int): The default cache duration in seconds (default is 300 seconds).

        Usage:
            cache = EmonicCache(cache_duration=600)
        """
        self.cache = {}
        self.cache_duration = cache_duration
    
    def _generate_key(self, func_name, args, kwargs):
        key = f"{func_name}#{args}#{kwargs}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get(self, timeout=None, key_prefix='Emonic', unless=None):
        """
        Decorator to retrieve a value from the cache or execute the function and cache the result.

        Args:
            timeout (int, optional): The cache timeout for this specific decorator (overrides the default).
            key_prefix (str, optional): The key prefix for cache entries (default is 'Emonic').
            unless (callable, optional): A condition function to determine whether to cache the result (default is None).

        Returns:
            callable: The decorator function.

        Usage:
            @cache.get(timeout=3600, key_prefix='my_cache', unless=lambda result: result is None)
            def my_function(*args, **kwargs):
                # Function logic here
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if timeout is None or time.time() - timestamp <= timeout:
                        return cached_result
                
                result = func(*args, **kwargs)
                if unless is None or not unless(result):
                    self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def clear_cache(self):
        """
        Clear the entire cache.

        Usage:
            cache.clear_cache()
        """
        self.cache = {}
    
    def delete(self, func_name, *args, **kwargs):
        """
        Delete a specific cache entry.

        Args:
            func_name (str): The name of the function for which to delete the cache entry.
            *args: Arguments to generate the cache entry key.
            **kwargs: Keyword arguments to generate the cache entry key.

        Usage:
            cache.delete('my_function', arg1, arg2, kwarg1=value)
        """
        key = self._generate_key(func_name, args, kwargs)
        if key in self.cache:
            del self.cache[key]
    
    def memoize(self, timeout=None, key_prefix='Emonic'):
        """
        Decorator to cache the result of a function with a specified timeout.

        Args:
            timeout (int, optional): The cache timeout for this specific decorator (overrides the default).
            key_prefix (str, optional): The key prefix for cache entries (default is 'Emonic').

        Returns:
            callable: The decorator function.

        Usage:
            @cache.memoize(timeout=3600, key_prefix='my_cache')
            def my_function(*args, **kwargs):
                # Function logic here
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if timeout is None or time.time() - timestamp <= timeout:
                        return cached_result
                
                result = func(*args, **kwargs)
                self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def set(self, func_name, value, *args, **kwargs):
        """
        Set a value in the cache.

        Args:
            func_name (str): The name of the function for which to set the cache value.
            value: The value to be cached.
            *args: Arguments to generate the cache entry key.
            **kwargs: Keyword arguments to generate the cache entry key.

        Usage:
            cache.set('my_function', 'cached_value', arg1, arg2, kwarg1=value)
        """
        key = self._generate_key(func_name, args, kwargs)
        self.cache[key] = (value, time.time())
    
    def get_or_set(self, timeout=None, key_prefix='Emonic'):
        """
        Decorator to retrieve a value from the cache or execute the function and cache the result if not found.

        Args:
            timeout (int, optional): The cache timeout for this specific decorator (overrides the default).
            key_prefix (str, optional): The key prefix for cache entries (default is 'Emonic').

        Returns:
            callable: The decorator function.

        Usage:
            @cache.get_or_set(timeout=3600, key_prefix='my_cache')
            def my_function(*args, **kwargs):
                # Function logic here
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if timeout is None or time.time() - timestamp <= timeout:
                        return cached_result
                
                result = func(*args, **kwargs)
                self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def cache_for(self, cache_duration):
        """
        Decorator to cache the result of a function for a specified duration.

        Args:
            cache_duration (int): The cache duration in seconds.

        Returns:
            callable: The decorator function.

        Usage:
            @cache.cache_for(3600)
            def my_function(*args, **kwargs):
                # Function logic here
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if time.time() - timestamp <= cache_duration:
                        return cached_result
                
                result = func(*args, **kwargs)
                self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def cache_unless(self, condition):
        """
        Decorator to cache the result of a function unless a condition is met.

        Args:
            condition (callable): A condition function that determines whether to cache the result.

        Returns:
            callable: The decorator function.

        Usage:
            @cache.cache_unless(lambda result: result is None)
            def my_function(*args, **kwargs):
                # Function logic here
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if not condition(cached_result):
                        return cached_result
                
                result = func(*args, **kwargs)
                if not condition(result):
                    self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
    
    def cache_if(self, condition):
        """
        Decorator to cache the result of a function if a condition is met.

        Args:
            condition (callable): A condition function that determines whether to cache the result.

        Returns:
            callable: The decorator function.

        Usage:
            @cache.cache_if(lambda result: result is not None)
            def my_function(*args, **kwargs):
                # Function logic here
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key = self._generate_key(func.__name__, args, kwargs)
                
                if key in self.cache:
                    cached_result, timestamp = self.cache[key]
                    if condition(cached_result):
                        return cached_result
                
                result = func(*args, **kwargs)
                if condition(result):
                    self.cache[key] = (result, time.time())
                return result
            
            return wrapper
        
        return decorator
