# django-middleware-request-id

The middleware detect if a client or the front reverse proxy server provides a X-Request-ID header, and get it as the request_id. If no such header is provided, it can provide a random value. 

## Install

```
pip install django-middleware-request-id
```

## Usage

*pro/settings.py*

```
INSTALLED_APPS = [
    "django_middleware_global_request",
    "django_middleware_request_id",
]

MIDDLEWARE = [
    ...
    "django_middleware_global_request.middleware.GlobalRequestMiddleware",
    "django_middleware_request_id.middlewares.DjangoMiddlewareRequestId",
    ...
]

```

*app/views.py*

```
from django.http import HttpResponse
from django_middleware_request_id import get_request_id

def get_request_id_view(request):
    request_id = get_request_id()
    return HttpResponse(request_id)

```

*app/urls.py*

```
from django.contrib import admin
from django.urls import path
froml . import views

urlpatterns = [
    path('get_request_id', views.get_request_id_view),
]

```

## Set the request id at nginx

```
http {
    ...
    # -------------------------------------------------------------------------------
    # Set variable $reqid.
    # If you trust client or front nginx's header, you can use `map block` here.
    # -------------------------------------------------------------------------------
    map $http_x_request_id $reqid {
        default $http_x_request_id;
        "" $request_id;
    }
    # -------------------------------------------------------------------------------

    server {

        # -------------------------------------------------------------------------------
        # If you don't trust client and front nginx's header, or you are sure this 
        # is the first front nginx, just set the variable $reqid to a new random value.
        # Use `map block` above, or use `set line` below, but don't use both.
        # Uncomment the `set line` below to `set new random value`.
        # -------------------------------------------------------------------------------
        # set $reqid $request_id;
        # -------------------------------------------------------------------------------

        ...
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header X-Request-Id $reqid;
            ...
        }
        ...
    }
}

```

## Releases

### v0.1.0

- First release.

### v0.1.2

- Fix problem that import `get_request_id` from the package root.
- Fix problem that NOT using DJANGO_REQUEST_ID_HEADER setting.
- Fix problem that call get_request_id() from none request context.

### v0.1.3

- Doc update.
