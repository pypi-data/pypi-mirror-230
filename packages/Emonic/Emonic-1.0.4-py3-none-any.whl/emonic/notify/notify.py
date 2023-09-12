import json
from werkzeug.wrappers import Response

class Notify:
    def __init__(self, app):
        self.app = app
        self.notifications = []

    def send(self, message, category='info', user_id=None, channel_id=None):
        notification = {'message': message, 'category': category}
        if user_id:
            notification['user_id'] = user_id
        if channel_id:
            notification['channel_id'] = channel_id
        self.notifications.append(notification)

    def _filter_notifications(self, notifications, category=None, user_id=None, channel_id=None):
        return [notification for notification in notifications
                if (category is None or notification['category'] == category) and
                (user_id is None or notification.get('user_id') == user_id) and
                (channel_id is None or notification.get('channel_id') == channel_id)]

    def get_notifications(self, category=None, user_id=None, channel_id=None):
        return self._filter_notifications(self.notifications, category, user_id, channel_id)

    def clear_notifications(self, category=None, user_id=None, channel_id=None):
        self.notifications = self._filter_notifications(self.notifications, category, user_id, channel_id)

    def inject_notifications(self, response):
        notifications = self.get_notifications()
        if notifications:
            response.data += json.dumps(notifications).encode('utf-8')
            response.headers['Content-Type'] = 'application/json'
            self.clear_notifications()
        return response

    def handle_errors(self, request, error):
        self.send(str(error), category='error')
        return Response('An error occurred!', content_type='text/plain', status=500)

    def __call__(self, environ, start_response):
        try:
            response = self.app(environ, start_response)
            return self.inject_notifications(response)
        except Exception as e:
            return self.handle_errors(environ, e)

    def notify_decorator(self, category='info', user_id=None, channel_id=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                message = f"Function '{func.__name__}' executed."
                self.send(message, category=category, user_id=user_id, channel_id=channel_id)
                return result
            return wrapper
        return decorator

    def info(self, message, user_id=None, channel_id=None):
        self.send(message, category='info', user_id=user_id, channel_id=channel_id)

    def success(self, message, user_id=None, channel_id=None):
        self.send(message, category='success', user_id=user_id, channel_id=channel_id)

    def warning(self, message, user_id=None, channel_id=None):
        self.send(message, category='warning', user_id=user_id, channel_id=channel_id)

    def error(self, message, user_id=None, channel_id=None):
        self.send(message, category='error', user_id=user_id, channel_id=channel_id)

    def user(self, message, user_id):
        self.send(message, category='user', user_id=user_id)

    def channel(self, message, channel_id):
        self.send(message, category='channel', channel_id=channel_id)

    def message(self, message, user_id, channel_id):
        self.send(message, category='message', user_id=user_id, channel_id=channel_id)