
DJANGO-RESTFRAMEWORK-AUTHENTICATION

DJANGO-RESTFRAMEWORK-AUTHENTICATION is an app to manage easily the authentication in Rest API. This library 
supports classical Django's and Json Web Token authentication, moreover it manages Google 0Auth 2.0 


Quick start


1. Add "authentication" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "rest_framework",
        "authentication",
    ]

    If you are using JWT add "rest_framework_simplejwt"::

        INSTALLED_APPS = [
            ...,
            "rest_framework",
            "authentication",
            "rest_framework_simplejwt",
        ]
2. Include the "authentication" URLconf in your project urls.py like this::

    path("api/", include("authentication.urls")),

3. GOOGLE OAUTH 2.0

To use Google OAuth 2.0 you must set in settings.py:

    GOOGLE_AUTHENTICATION = True
    GOOGLE_AUTHENTICATION_CLIENT_ID = "your_client_id"
    GOOGLE_AUTHENTICATION_CLIENT_SECRET = "your_client_secret"

You should set GOOGLE_AUTHENTICATION_CLIENT_SECRET as enviroment variable because it is a sensible information.

4. JWT AUTHENTICATION

To use JWT authentication you must set in settings.py:

    JWT_AUTHENTICATION = True

Remember add rest_framework_simplejwt to INSTALLED_APPS.

You are free to use the authentication system that you wan. You can use either Google OAuth or JWT, and you can use both as well.