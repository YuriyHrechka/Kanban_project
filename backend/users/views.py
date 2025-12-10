from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserAuthSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import ScopedRateThrottle

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name="dispatch")
class RegisterAPIView(APIView):
    """Register a new user and return authentication tokens."""

    serializer_class = UserAuthSerializer
    throttle_classes = [ScopedRateThrottle]
    permission_classes = [AllowAny]
    throttle_scope = "register"

    def post(self, request):
        """
        Handle user registration.

        :param request: The HTTP request containing user registration data.
        :return: A JSON response with refresh/access tokens and user details.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_id": user.id,
                "username": user.username,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileAPIView(APIView):
    """Retrieve the profile of the authenticated user."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        """
        Retrieve the profile of the authenticated user.

        :param request: The HTTP request made by an authenticated user.
        :return: A JSON response with the user's profile data.
        """
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
