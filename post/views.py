from datetime import datetime
import base64

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated

from post.models import Tag, Comment, Post
from post.serializers import (
    TagSerializer,
    CommentSerializer,
    CommentListSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostLikeSerializer,
    PostScheduleSerializer,
)
from post.permissions import (
    IsAdminOrIfAuthenticatedReadOnly,
    IsPostCreatorOrReadOnly,
    IsCommentWriterOrReadOnly,
)
from post.tasks import create_post


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


class CommentManageViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsCommentWriterOrReadOnly)


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsPostCreatorOrReadOnly)
    pagination_class = PostDefaultPagination

    def get_serializer_class(self):
        if self.action in (
            "list",
            "liked_posts",
            "user_posts",
            "followings_posts",
        ):
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "comment":
            return CommentSerializer
        if self.action == "comments":
            return CommentSerializer
        if self.action == "like_post":
            return PostLikeSerializer
        if self.action == "schedule":
            return PostScheduleSerializer
        return PostSerializer

    @staticmethod
    def _params_to_ints(qs: str) -> list:
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self) -> QuerySet:
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

    def perform_create(self, serializer) -> None:
        serializer.save(creator=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="like",
    )
    def like_post(self, request, pk=None) -> Response:
        """The user likes or unlikes specified post"""
        item = self.get_object()
        user = request.user

        if user in item.likes.all():
            item.likes.remove(user)
            message = {"message": "You successfully unliked this post."}
        else:
            item.likes.add(user)
            message = {"message": "You successfully liked this post."}
        item.save()

        return Response(message, status=status.HTTP_201_CREATED)

    @action(
        methods=["GET", "POST"],
        detail=True,
        url_path="comments",
    )
    def comments(self, request, pk=None) -> Response:
        """Get a list of comments or create new comment for specified post"""
        item = self.get_object()
        user = request.user

        if request.method == "GET":
            queryset = Comment.objects.filter(post=item)
            serializer = CommentListSerializer(
                queryset, many=True, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            serializer = CommentSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save(writer=user, post=item)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"error": "Method not allowed"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked",
    )
    def liked_posts(self, request) -> Response:
        """The user receives all the posts which he has liked"""
        queryset = request.user.liked_posts
        serializer = PostListSerializer(
            queryset, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="my",
    )
    def user_posts(self, request) -> Response:
        """The user receives all his/her posts"""
        queryset = request.user.created_posts
        serializer = PostListSerializer(
            queryset, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=False,
        url_path="followings",
    )
    def followings_posts(self, request) -> Response:
        """The user receives all the posts of the users he/she follows"""
        following_users = request.user.follows.all()
        queryset = self.queryset.filter(creator__in=following_users)
        serializer = PostListSerializer(
            queryset, many=True, context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=False,
        url_path="schedule",
    )
    def schedule(self, request) -> Response:
        """The user creating a scheduled post with specified date and time"""
        serializer = PostSerializer(data=request.data)
        creator_id = request.user.id

        if serializer.is_valid():
            # Schedule post creation task
            tag_ids = [tag.id for tag in serializer.validated_data.pop("tags", [])]
            image = base64.b64encode(serializer.validated_data.pop("image").read())
            scheduled_time = datetime.strptime(
                request.data["scheduled_time"], "%Y-%m-%dT%H:%M"
            ).astimezone()

            create_post.apply_async(
                args=[serializer.validated_data, creator_id, tag_ids, image],
                eta=scheduled_time,
            )

            return Response(
                {"message": "Post scheduled successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by title insensitive contains",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                "tags",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by tag ids (ex. ?tags=4,7)",
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List posts with filter by title or tags"""
        return super().list(request, *args, **kwargs)
