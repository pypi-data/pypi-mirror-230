from functools import wraps
from datetime import datetime, timedelta
from werkzeug.wrappers import Response

class Limiter:
    def __init__(self, app=None):
        self.app = app
        self.default_limit = 100
        self.default_period = 60
        self.default_error_message = 'Rate limit exceeded'
        self.strategies = {}
        self.cache = {}
        self.whitelisted_ips = set()

    def limit(self, limit=None, period=None, error_message=None, strategy=None):
        """
        Decorator for rate limiting.

        Args:
            limit (int or callable): The request limit within the period.
            period (int or callable): The time period in seconds.
            error_message (str): The error message to return on rate limit exceed.
            strategy (str): The rate limiting strategy to use.

        Usage:
            @limiter.limit(limit=100, period=60, error_message='Rate limit exceeded')
            def my_handler(request):
                return Response('OK')
        """
        def decorator(handler):
            @wraps(handler)
            def wrapped_handler(request, *args, **kwargs):
                key = self.get_key(request)
                now = datetime.now()

                limit_value = limit(request) if callable(limit) else (limit if limit is not None else self.default_limit)
                period_value = period(request) if callable(period) else (period if period is not None else self.default_period)

                if key in self.cache:
                    requests = self.cache[key]
                    valid_requests = [
                        req for req in requests if (now - req) <= timedelta(seconds=period_value)
                    ]

                    if len(valid_requests) >= limit_value:
                        message = error_message if error_message else self.default_error_message
                        return self.error_response(message, error_code='RATE_LIMIT_EXCEEDED')

                    valid_requests.append(now)
                    self.cache[key] = valid_requests
                else:
                    self.cache[key] = [now]

                return handler(request, *args, **kwargs)

            return wrapped_handler

        return decorator

    def get_key(self, request):
        """
        Get a key for identifying the client (e.g., IP address).

        Args:
            request: The incoming request object.

        Returns:
            str: The client key.

        Usage:
            key = self.get_key(request)
        """
        return request.remote_addr

    def strategy(self, name, storage):
        """
        Decorator to define a rate limiting strategy.

        Args:
            name (str): The name of the strategy.
            storage: The storage backend for the strategy.

        Usage:
            @limiter.strategy('my_strategy', storage)
            def my_strategy_function(key, limit, period):
                # Implement the rate limiting strategy logic.
                pass
        """
        def decorator(f):
            self.strategies[name] = storage
            return f
        return decorator

    def hit(self, key, amount=1):
        """
        Record a request hit for rate limiting.

        Args:
            key (str): The client key.
            amount (int): The number of hits to record.

        Usage:
            limiter.hit('client_key', amount=1)
        """
        now = datetime.now()
        if key in self.cache:
            requests = self.cache[key]
            valid_requests = [
                req for req in requests if (now - req) <= timedelta(seconds=self.default_period)
            ]
            valid_requests.extend([now] * amount)
            self.cache[key] = valid_requests
        else:
            self.cache[key] = [now] * amount

    def reset(self, key):
        """
        Reset rate limiting for a client key.

        Args:
            key (str): The client key.

        Usage:
            limiter.reset('client_key')
        """
        if key in self.cache:
            del self.cache[key]

    def reset_all(self):
        """
        Reset rate limiting for all clients.

        Usage:
            limiter.reset_all()
        """
        self.cache = {}

    def get_remaining_hits(self, key):
        """
        Get the remaining allowed hits for a client key.

        Args:
            key (str): The client key.

        Returns:
            int: The remaining allowed hits.

        Usage:
            remaining_hits = limiter.get_remaining_hits('client_key')
        """
        if key in self.cache:
            requests = self.cache[key]
            valid_requests = [
                req for req in requests if (datetime.now() - req) <= timedelta(seconds=self.default_period)
            ]
            return self.default_limit - len(valid_requests)
        return self.default_limit

    def get_time_until_reset(self, key):
        """
        Get the time until rate limiting resets for a client key.

        Args:
            key (str): The client key.

        Returns:
            timedelta: The time until rate limiting resets.

        Usage:
            time_until_reset = limiter.get_time_until_reset('client_key')
        """
        if key in self.cache:
            requests = self.cache[key]
            latest_request_time = max(requests)
            reset_time = latest_request_time + timedelta(seconds=self.default_period)
            time_until_reset = reset_time - datetime.now()
            return max(time_until_reset, timedelta(seconds=0))
        return timedelta(seconds=0)

    def burst_limit(self, burst_limit=None, burst_period=None, error_message=None):
        """
        Decorator for burst rate limiting.

        Args:
            burst_limit (int or callable): The burst request limit.
            burst_period (int or callable): The burst period in seconds.
            error_message (str): The error message on burst limit exceed.

        Usage:
            @limiter.burst_limit(burst_limit=10, burst_period=10, error_message='Burst limit exceeded')
            def my_handler(request):
                return Response('OK')
        """
        def decorator(handler):
            @wraps(handler)
            def wrapped_handler(request, *args, **kwargs):
                key = self.get_key(request)
                now = datetime.now()

                burst_limit_value = (
                    burst_limit(request) if callable(burst_limit) else (burst_limit if burst_limit is not None else self.default_limit)
                )
                burst_period_value = (
                    burst_period(request) if callable(burst_period) else (burst_period if burst_period is not None else self.default_period)
                )

                if key in self.cache:
                    requests = self.cache[key]
                    valid_burst_requests = [
                        req for req in requests if (now - req) <= timedelta(seconds=burst_period_value)
                    ]

                    if len(valid_burst_requests) >= burst_limit_value:
                        message = error_message if error_message else self.default_error_message
                        return self.error_response(message, error_code='BURST_LIMIT_EXCEEDED')

                return handler(request, *args, **kwargs)

            return wrapped_handler

        return decorator

    def rate_limit_tier(self, tier_conditions, period=None, strategy=None):
        """
        Decorator for applying rate limiting tiers.

        Args:
            tier_conditions (list): List of rate limit conditions and limits.
            period (int or callable): The time period in seconds.
            strategy (str): The rate limiting strategy to use.

        Usage:
            tier_conditions = [
                (condition1, burst_condition1, limit1, burst_limit1),
                (condition2, burst_condition2, limit2, burst_limit2),
                # Add more rate limit tiers as needed.
            ]

            @limiter.rate_limit_tier(tier_conditions, period=60, strategy='my_strategy')
            def my_handler(request):
                return Response('OK')
        """
        def decorator(handler):
            @wraps(handler)
            def wrapped_handler(request, *args, **kwargs):
                for limit_condition, burst_condition, tier_limit, tier_burst in tier_conditions:
                    if limit_condition(request):
                        return self.limit(limit=tier_limit, period=period, strategy=strategy)(handler)(request, *args, **kwargs)
                    if burst_condition(request):
                        return self.burst_limit(burst_limit=tier_burst, strategy=strategy)(handler)(request, *args, **kwargs)
                return handler(request, *args, **kwargs)

            return wrapped_handler

        return decorator

    def error_response(self, message, status_code=429, error_code=None):
        """
        Create an error response for rate limiting exceed.

        Args:
            message (str): The error message.
            status_code (int): The HTTP status code for the error response.
            error_code (str): The error code to include in the response.

        Returns:
            Response: The error response.

        Usage:
            response = limiter.error_response('Rate limit exceeded', status_code=429, error_code='RATE_LIMIT_EXCEEDED')
        """
        response = Response(message, status=status_code)
        response.headers['X-Error-Code'] = error_code
        return response

    def whitelist_ip(self, ip):
        """
        Whitelist an IP address.

        Args:
            ip (str): The IP address to whitelist.

        Usage:
            limiter.whitelist_ip('127.0.0.1')
        """
        self.whitelisted_ips.add(ip)

    def is_ip_whitelisted(self, ip):
        """
        Check if an IP address is whitelisted.

        Args:
            ip (str): The IP address to check.

        Returns:
            bool: True if the IP is whitelisted, False otherwise.

        Usage:
            is_whitelisted = limiter.is_ip_whitelisted('127.0.0.1')
        """
        return ip in self.whitelisted_ips

    def ip_whitelist(self, handler):
        """
        Decorator to restrict access to whitelisted IPs only.

        Args:
            handler: The request handler to protect with IP whitelisting.

        Usage:
            @limiter.ip_whitelist
            def my_handler(request):
                return Response('OK')
        """
        @wraps(handler)
        def wrapped_handler(request, *args, **kwargs):
            key = self.get_key(request)
            if self.is_ip_whitelisted(key):
                return handler(request, *args, **kwargs)
            return self.error_response('Forbidden', status_code=403, error_code='FORBIDDEN')

        return wrapped_handler
