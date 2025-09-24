from django.urls import path, include

from users.views import RegisterAPIView, ProfileAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("register/", RegisterAPIView.as_view(), name="auth_register"),
    path("profile/", ProfileAPIView.as_view(), name="user_profile"),
]
