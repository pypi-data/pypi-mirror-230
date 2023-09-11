from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('auth/signup/',views.UserCreationView.as_view(),name="signup"),
    path("auth/user/", views.UserDetailsUpdateView.as_view(), name="user-detail-update"),
    path("auth/changepassword/",views.UserChangePasswordView.as_view(),name="change-password"),
]

try:
    JWT_AUTHENTICATION = settings.JWT_AUTHENTICATION
except AttributeError:
    JWT_AUTHENTICATION = False
    
try:
    GOOGLE_AUTHENTICATION = settings.GOOGLE_AUTHENTICATION
except AttributeError:
    GOOGLE_AUTHENTICATION = False

if JWT_AUTHENTICATION:
    from rest_framework_simplejwt import views as jwt_views
    
    urlpatterns += [
        path('auth/token/',jwt_views.TokenObtainPairView.as_view(),name="token-obtain"),
        path('auth/token/refresh/',jwt_views.TokenRefreshView.as_view(),name="token-refresh"),
    ]
else:
    urlpatterns.append(path("auth/login/",views.UserLoginView.as_view(),name="login"))
    
if GOOGLE_AUTHENTICATION:
    urlpatterns += [
        path("auth/google/", views.UserGoogleLogin.as_view(), name="google-login"),
        path("auth/google/callback/",views.UserGoogleLoginCallback.as_view(), name="google-callback")
    ]

