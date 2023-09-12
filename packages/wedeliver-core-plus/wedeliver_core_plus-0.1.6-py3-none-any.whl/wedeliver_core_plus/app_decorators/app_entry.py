from functools import wraps

from wedeliver_core_plus import WedeliverCorePlus
from wedeliver_core_plus.app_decorators import (
    handle_response,
    handle_auth,
    handle_exceptions,
    serializer,
)
# from wedeliver_core_plus.helpers.get_prefix import get_prefix


def route(path, methods=["GET"], schema=None, many=False, allowed_roles=None, require_auth=True,
          append_auth_args=None,
          pre_login=False,
          allowed_permissions=None):
    app = WedeliverCorePlus.get_app()

    def factory(func):
        @app.route(path, methods=methods)
        @handle_response
        @handle_exceptions
        @handle_auth(require_auth=require_auth, append_auth_args=append_auth_args, allowed_roles=allowed_roles,
                     allowed_permissions=allowed_permissions, pre_login=pre_login)
        @serializer(schema=schema, many=many)
        @wraps(func)
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)

        return decorator

    return factory
