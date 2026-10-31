from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """Register new users and return their authentication token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate registration data and create a user."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        response_data = {
            "token": token.key,
            "fullname": user.get_full_name(),
            "email": user.email,
            "user_id": user.id,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Return a token and user information for valid credentials."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Validate login data and reuse or create the user's token."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        response_data = {
            "token": token.key,
            "fullname": user.get_full_name(),
            "email": user.email,
            "user_id": user.id,
        }
        return Response(response_data, status=status.HTTP_200_OK)
