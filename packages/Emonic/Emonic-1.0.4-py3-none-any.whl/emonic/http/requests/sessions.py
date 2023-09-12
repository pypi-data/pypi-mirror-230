class Session:
    def __init__(self, api_request):
        self.api_request = api_request

    def get(self, url, headers=None, params=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.get(url, headers=headers, params=params, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def post(self, url, headers=None, data=None, json_data=None, files=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.post(url, headers=headers, data=data, json_data=json_data, files=files, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def put(self, url, headers=None, data=None, json_data=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.put(url, headers=headers, data=data, json_data=json_data, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def delete(self, url, headers=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.delete(url, headers=headers, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def head(self, url, headers=None, params=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.head(url, headers=headers, params=params, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def patch(self, url, headers=None, data=None, json_data=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.patch(url, headers=headers, data=data, json_data=json_data, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def options(self, url, headers=None, params=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.options(url, headers=headers, params=params, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def request(self, method, url, headers=None, params=None, data=None, json_data=None, files=None, timeout=None, retries=None, use_cache=True, auth=None):
        return self.api_request.request(method, url, headers=headers, params=params, data=data, json_data=json_data, files=files, timeout=timeout, retries=retries, use_cache=use_cache, auth=auth)

    def session(self):
        return self.api_request.create_session()

    def set_default_timeout(self, timeout):
        self.api_request.set_default_timeout(timeout)

    def set_max_redirects(self, max_redirects):
        self.api_request.set_max_redirects(max_redirects)