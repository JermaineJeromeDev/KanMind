"""
Views for the auth_app.
Handles user registration, login, and email existence checks.
"""

# 2. Third-party (Django & DRF)
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# 3. Local
from .serializers import RegistrationSerializer, UserPublicSerializer

User = get_user_model()


class RegistrationView(APIView):
    """
    Handles new user registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Creates a new user and returns an authentication token.
        """
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                self._format_user_data(user, token),
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"error": "Ungültige Anfragedaten."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def _format_user_data(self, user, token):
        """
        Formats user response data.
        """
        return {
            "token": token.key,
            "fullname": user.fullname,
            "email": user.email,
            "user_id": user.id
        }


class LoginView(APIView):
    """
    Handles user authentication.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Authenticates user and returns token.
        """
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                self._format_login_data(user, token),
                status=status.HTTP_200_OK
            )
        return Response(
            {"error": "Ungültige Anfragedaten."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def _format_login_data(self, user, token):
        """
        Formats login response data.
        """
        return {
            "token": token.key,
            "fullname": user.fullname,
            "email": user.email,
            "user_id": user.id
        }


class EmailCheckView(APIView):
    """
    Checks if an email is already registered.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieves user by email or returns 404.
        """
        email = request.query_params.get('email')
        if not email:
            return Response(
                {"error": "Ungültige Anfrage. Die E-Mail-Adresse fehlt oder hat ein falsches Format."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self._get_user_response(email)

    def _get_user_response(self, email):
        """
        Fetches user or returns error message.
        """
        try:
            user = User.objects.get(email=email)
            serializer = UserPublicSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "Email nicht gefunden. Die Email exestiert nicht."},
                status=status.HTTP_404_NOT_FOUND
            )
