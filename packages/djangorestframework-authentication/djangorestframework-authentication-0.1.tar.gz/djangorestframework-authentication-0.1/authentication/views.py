from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, login
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.forms import AuthenticationForm
from django.utils.crypto import get_random_string
from .serializers import UserSerializer, UserCreationSerializer, UserChangePasswordSerializer, UserUpdateSerializer
import requests

# Create your views here.
User = get_user_model()

try:
    JWT_AUTHENTICATION = settings.JWT_AUTHENTICATION
except AttributeError:
    JWT_AUTHENTICATION = False
    
try:
    GOOGLE_AUTHENTICATION = settings.GOOGLE_AUTHENTICATION
    client_id = settings.GOOGLE_AUTHENTICATION_CLIENT_ID
    client_secret = settings.GOOGLE_AUTHENTICATION_CLIENT_SECRET
except AttributeError:
    GOOGLE_AUTHENTICATION = False
    


class UserCreationView(CreateAPIView):
    serializer_class = UserCreationSerializer


class UserDetailsUpdateView(RetrieveUpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return super().get_serializer_class()

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


class UserChangePasswordView(UpdateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserChangePasswordSerializer

    def get_object(self):
        return User.objects.get(pk=self.request.user.pk)


class UserLoginView(APIView):
    def post(self, request):
        form = AuthenticationForm(request, data=request.data)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(data=form.errors.as_json(), status=status.HTTP_401_UNAUTHORIZED)


class UserGoogleLogin(APIView):

    def get(self, request):
        state = get_random_string(length=12)
        request.session["state"] = state
        redirect_uri = f"{request.scheme}%3A%2F%2F{request.get_host()}%2Fauth%2Fgoogle%2Fcallback%2F"
        url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&state={state}&redirect_uri={redirect_uri}&response_type=code&scope=email%20profile%20profile%20openid"
        return redirect(url)

class UserGoogleLoginCallback(APIView):
    def verify_state(self,state):
        return self.request.session["state"] == state
    
    def get(self, request):

        code = request.GET.get("code")
        state = request.GET.get("state")
        print(request.session["state"])
        if not self.verify_state(state):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{request.scheme}://{request.get_host()}/auth/google/callback/",
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()
        token_info_url = "https://oauth2.googleapis.com/tokeninfo"
        response = requests.get(
            token_info_url, {"id_token": token_data.get("id_token")})
        user_data = response.json()
        email: str = user_data.get('email')
        user = User.objects.filter(email=email).first()
        
        if user:
            if JWT_AUTHENTICATION:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token
                return Response({"refresh_token": str(refresh_token), "access_token": str(access_token)})
            
            login(request, user)
            serializer = UserSerializer(user)
            return Response(serializer.data)

        user_data = {
            "username": email.split("@")[0],
            "email": email,
            "first_name": user_data.get("given_name"),
            "last_name": user_data.get("family_name"),
            "password": get_random_string(12),
        }
        serializer = UserCreationSerializer(data=user_data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(email=email)
            if JWT_AUTHENTICATION:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token
                return Response({"refresh_token": str(refresh_token), "access_token": str(access_token)})
            login(request,user)
            return Response(serializer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)
