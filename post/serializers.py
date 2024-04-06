from rest_framework import serializers

from post.models import Tag, Comment, Post


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "created_at",
        )


class CommentListSerializer(serializers.ModelSerializer):
    writer = serializers.HyperlinkedRelatedField(
        view_name="user:manage",
        read_only=True,
        many=False,
    )

    class Meta:
        model = Comment
        fields = (
            "id",
            "writer",
            "post",
            "content",
            "created_at",
        )


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "image",
            "title",
            "content",
            "tags",
            "created_at",
        )


class PostListSerializer(PostSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    count_likes = serializers.IntegerField(read_only=True)
    creator = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="user:manage",
    )
    comments = serializers.HyperlinkedIdentityField(view_name="post:post-comments")

    class Meta:
        model = Post
        fields = (
            "id",
            "image",
            "title",
            "content",
            "creator",
            "tags",
            "created_at",
            "count_likes",
            "comments",
        )


class PostDetailSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    count_likes = serializers.IntegerField(read_only=True)
    creator = serializers.HyperlinkedRelatedField(
        many=False,
        read_only=True,
        view_name="user:manage",
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "image",
            "title",
            "content",
            "creator",
            "tags",
            "created_at",
            "count_likes",
            "comments",
        )


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id",)


class PostScheduleSerializer(serializers.ModelSerializer):
    scheduled_time = serializers.DateTimeField()

    class Meta:
        model = Post
        fields = (
            "id",
            "scheduled_time",
            "image",
            "title",
            "content",
            "tags",
        )
