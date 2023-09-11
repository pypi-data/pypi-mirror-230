
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


