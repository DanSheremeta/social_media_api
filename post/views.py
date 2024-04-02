from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from post.models import Tag, Comment, Post
from post.serializers import (
    TagSerializer,
    CommentSerializer,
    CommentListSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
)
from post.permissions import IsAdminOrIfAuthenticatedReadOnly


class PostDefaultPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class TagViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)
    pagination_class = PostDefaultPagination

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "comment":
            return CommentSerializer
        return PostSerializer

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the posts with filters"""
        title = self.request.query_params.get("title")
        tags = self.request.query_params.get("tags")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if tags:
            tags_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tags_ids)

        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like-post",
    )
    def like_post(self, request, pk=None):
        item = self.get_object()
        user = request.user

        if user in item.likes.all():
            item.likes.remove(user)
        else:
            item.likes.add(user)
        item.save()

        return Response(status=status.HTTP_201_CREATED)

    @action(
        methods=["POST"],
        detail=True,
        url_path="comment",
    )
    def comment(self, request, pk=None):
        item = self.get_object()
        user = request.user
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(writer=user, post=item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["GET"],
        detail=True,
        url_path="comments",
    )
    def comments(self, request, pk=None):
        item = self.get_object()
        queryset = Comment.objects.filter(post=item)
        serializer = CommentListSerializer(
            queryset, many=True, context={"request": request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
