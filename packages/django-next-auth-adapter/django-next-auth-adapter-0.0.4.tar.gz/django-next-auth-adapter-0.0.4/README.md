# Django Next Auth Adapter

Django Next Auth Adapter is a Django package designed to handle server-side requests from the "next-auth-http-adapter" JavaScript package. This package is intended for use with Next.js and NextAuth.js to seamlessly integrate custom backend functionality into the NextAuth.js authentication flow by facilitating HTTP communication between the frontend and backend.

## Pre-requisites

### User Model

add the following to your user model

```python

class User(AbstractBaseUser):
    # ...
    email_verified = models.DateTimeField(blank=True, null=True)
    # ...
    EMAIL_FIELD = "email"
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    # ...

```

## Installation

You can install the package via pip:

```bash
pip install django-next-auth-adapter
```

## Configuration

To configure the Django Next Auth Adapter, you need to define certain settings in your Django project's settings module (`settings.py`).

Include `django_next_auth_adapter` in your `INSTALLED_APPS`:

```python
# settings.py

INSTALLED_APPS = [
    # Your other installed apps
    "django_next_auth_adapter",
]
```

For custom configuration, add the following settings to your `settings.py` file:

```python
# settings.py

DJANGO_NEXT_AUTH_ADAPTER = {
    # optional: specify the permission classes applied to views within the package. Customize these classes as needed to control access to your views. Do not specify this parameter if you want to use the default permission classes.
    "PERMISSION_CLASSES": [
        # Add your permission classes here
    ],
    # optional: specify the token used for authenticating requests from the next-auth server. If not provided, authentication will be bypassed.
    "REMOTE_AUTH_TOKEN": "your-remote-auth-token",
}
```

### Available Settings

-   **DJANGO_NEXT_AUTH_ADAPTER (dictionary):** The main configuration dictionary for the package.
    -   **PERMISSION_CLASSES (list):** This is a list of permission classes applied to views within the package. Customize these classes as needed to control access to your views.
    -   **REMOTE_AUTH_TOKEN (string, optional):** The token used by the default permission class for authenticating requests from the next-auth server. If not provided, authentication will be bypassed.

## Usage

To use the Django Next Auth Adapter, import it as follows:

```python
from django_next_auth_adapter import DjangoNextAuthAdapter
```

You can then use the imported classes and functions to handle authentication and authorization as needed within your Django views.

## Configuration in `urls.py`

To include the package's URLs in your Django project, follow these steps:

1. Open your project's base `urls.py` file.

2. Import the package's views and include them in your URL patterns.

```python
# urls.py

from django.urls import path, include
from django_next_auth_adapter.views import YourViewName1, YourViewName2  # Import your views here

urlpatterns = [
    # Your other URL patterns
    path('next-auth/', include('django_next_auth_adapter.urls')),  # Include the package's URLs here
]
```

## Signals

The package provides the following signals that you can use to customize the authentication and authorization process:

-   **user_created:** Sent when a new user is created. The signal sends the following arguments:
    -   **sender:** The serializer class.
    -   **user:** The user instance.
    -   **validated_data:** The validated data used to create the user.
    -   **image:** The image url of the user.
    -   **name:** The name of the user.
-   **user_updated:** Sent when a user is updated. The signal sends the following arguments:
    -   **sender:** The serializer class.
    -   **user:** The user instance.
    -   **validated_data:** The validated data used to create the user.
    -   **image:** The image url of the user.
    -   **name:** The name of the user.

## Links

-   [GitHub Repository](https://github.com/mabdullahadeel/django-next-auth-adapter)
-   [next-auth-http-adapter](https://github.com/mabdullahadeel/next-auth-http-adapter)

## License

This project is open source and is licensed under the MIT License.
