from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from user.permissions import IsOwnerOrReadOnly
from user.serializers import (
    AuthTokenSerializer,
    UserSerializer,
    UserListSerializer,
)


class FollowUserView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=None,
        responses={
            status.HTTP_201_CREATED: {"type": "message"},
            status.HTTP_400_BAD_REQUEST: {"type": "error"},
        },
        methods=["POST"]
    )
    def post(self, request, pk=None):
        """The user follows another user"""
        user_to_follow = get_object_or_404(get_user_model(), pk=pk)
        if request.user == user_to_follow:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.follows.add(user_to_follow)
        return Response(
            {"message": "User followed successfully."}, status=status.HTTP_201_CREATED
        )

    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        methods=["DELETE"]
    )
    def delete(self, request, pk=None):
        """The user unfollows another user"""
        user_to_unfollow = get_object_or_404(get_user_model(), pk=pk)
        if request.user == user_to_unfollow:
            return Response(
                {"error": "You cannot unfollow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.follows.remove(user_to_unfollow)
        return Response(
            {"message": "User unfollowed successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class UserListPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    pagination_class = UserListPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        username = self.request.query_params.get("username")

        if username:
            queryset = queryset.filter(username__icontains=username)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                description="Filter by username insensitive contains",
                required=False,
                type=str,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        """List users with filter by username"""
        return self.list(request, *args, **kwargs)


class ManageUserView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserListSerializer
    permission_classes = (
        IsAuthenticated,
        IsOwnerOrReadOnly,
    )


class LogoutUserView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=None,
        responses={status.HTTP_204_NO_CONTENT: None},
        methods=["DELETE"]
    )
    def delete(self, request):
        """Delete user's token"""
        token = Token.objects.get(user_id=request.user.id)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
