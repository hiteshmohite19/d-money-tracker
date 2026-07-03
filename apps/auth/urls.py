from django.urls import path

from .views import AuthViewSet

auth_register = AuthViewSet.as_view({"post": "register"})
auth_login = AuthViewSet.as_view({"post": "login"})
auth_signin = AuthViewSet.as_view({"post": "signin"})
auth_refresh_token = AuthViewSet.as_view({"post": "refresh_token"})

urlpatterns = [
    path("register/", auth_register, name="auth-register"),
    path("login/", auth_login, name="auth-login"),
    path("signin/", auth_signin, name="auth-signin"),
    path("refresh-token/", auth_refresh_token, name="auth-refresh-token"),
]
