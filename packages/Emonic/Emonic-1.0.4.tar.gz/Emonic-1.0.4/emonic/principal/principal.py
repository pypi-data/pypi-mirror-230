from werkzeug.wrappers import Response

access_denied = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Access Denied!</title>
</head>
<body>
    <h1>Access Denied!</h1>
    <p>Your request can't proceed!</p>
</body>
</html>'''

class PrincipalContext:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.principal = self


class Identity:
    def __init__(self, id):
        self.id = id
        self.roles = set()
        self.permissions = set()

    def has_role(self, role):
        return role in self.roles

    def has_permission(self, permission):
        return permission in self.permissions


class Permission:
    def __init__(self, name):
        self.name = name


class Role:
    def __init__(self, name):
        self.name = name
        self.permissions = set()

    def add_permission(self, permission):
        self.permissions.add(permission)


class PrincipalPermission:
    def __init__(self, permission):
        self.permission = permission

    def __call__(self, view_func):
        def wrapper(request, **values):
            identity = getattr(request, 'identity', None)
            if identity and identity.has_permission(self.permission):
                return view_func(request, **values)
            else:
                response_content = access_denied(request)
                return Response(response_content, content_type='text/html', status=403)

        return wrapper
    
class AnonymousIdentity(Identity):
    def __init__(self):
        super().__init__(id=None)
        self.roles.add('anonymous')

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True
    
class Principal:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self._identity_loaded_signal = Signal()
        self._identity_changed_signal = Signal()
        app.principal = self
        app.before_request(self._load_identity)
        app.after_request(self._clear_identity)

    def unauthorized_handler(self, func):
        self._unauthorized_callback = func
        return func

    def permission_required(self, permission):
        def decorator(view_func):
            @PrincipalPermission(permission)
            def wrapper(request, **values):
                return view_func(request, **values)
            return wrapper
        return decorator

    def role_required(self, role):
        def decorator(view_func):
            @PrincipalPermission(role)
            def wrapper(request, **values):
                return view_func(request, **values)
            return wrapper
        return decorator

    def unauthorized(self):
        if self._unauthorized_callback:
            return self._unauthorized_callback()
        return Response("Unauthorized", status=401)
    
class Signal:
    def __init__(self):
        self.handlers = []

    def connect(self, handler):
        self.handlers.append(handler)

    def send(self, sender, **kwargs):
        for handler in self.handlers:
            handler(sender, **kwargs)
