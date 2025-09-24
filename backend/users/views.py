from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserAuthSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle


class RegisterAPIView(APIView):
    """Register a new user and return tokens."""

    serializer_class = UserAuthSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'register'

    def post(self, request):
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
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
