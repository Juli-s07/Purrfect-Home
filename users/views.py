from django.contrib.auth.models import User
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer

import logging
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(email__iexact=serializer.validated_data["email"]).exists():
            logger.warning("Registration rejected: email has been already taken")
            return Response({"email": ["This email has already been taken."]},
                            status=status.HTTP_409_CONFLICT)
        user = serializer.save()
        logger.info("User has been registered: user_id=%s", user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        u = request.user
        return Response({
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "email": u.email,
            "date_joined": u.date_joined,
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh")).blacklist()
        except TokenError:
            logger.warning("Logout rejected: refresh token is invalid, user_id=%s", request.user.id)
            return Response({"detail": ["Invalid token"]},)
        logger.info("User has logged out: user_id=%s", request.user.id)
        return Response(status=205)
