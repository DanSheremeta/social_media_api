from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status

from post.models import Tag, Comment, Post
from post.serializers import PostListSerializer, PostSerializer, CommentListSerializer, CommentSerializer

POST_URL = reverse("post:post-list")


def sample_tag(**params) -> Tag:
    defaults = {"name": "Test Tag"}
    defaults.update(params)
    return Tag.objects.create(**defaults)


def sample_comment_for_post(**params) -> Comment:
    defaults = {
        "content": "Test Comment",
    }
    defaults.update(params)
    return Comment.objects.create(**defaults)


def sample_post(**params) -> Post:
    defaults = {
        "title": "Test Post",
        "content": "Some text...",
    }
    defaults.update(params)
    return Post.objects.create(**defaults)


class UnauthenticatedPostApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_posts(self):
        sample_post(creator=self.user)
        sample_post(creator=self.user)

        request = self.factory.get(POST_URL)
        res = self.client.get(POST_URL)

        posts = Post.objects.order_by("created_at")
        serializer = PostListSerializer(posts, many=True, context={"request": request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_posts_by_tags(self):
        tag1 = sample_tag(name="Tag 1")
        tag2 = sample_tag(name="Tag 2")

        post1 = sample_post(
            title="Post 1",
            creator=self.user,
        )
        post2 = sample_post(
            title="Post 2",
            creator=self.user,
        )
        post3 = sample_post(
            title="Post 3",
            creator=self.user,
        )

        post1.tags.add(tag1)
        post2.tags.add(tag2)

        request = self.factory.get(POST_URL, {"tags": f"{tag1.id},{tag2.id}"})
        res = self.client.get(POST_URL, {"tags": f"{tag1.id},{tag2.id}"})

        serializer1 = PostListSerializer(post1, context={"request": request})
        serializer2 = PostListSerializer(post2, context={"request": request})
        serializer3 = PostListSerializer(post3, context={"request": request})

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_filter_posts_by_title(self):
        post1 = sample_post(
            title="Test Post 1",
            creator=self.user,
        )
        post2 = sample_post(
            title="Test Post 2",
            creator=self.user,
        )
        post3 = sample_post(
            title="Another Post 3",
            creator=self.user,
        )

        request = self.factory.get(POST_URL, {"title": "Test"})
        res = self.client.get(POST_URL, {"title": "Test"})

        serializer1 = PostListSerializer(post1, context={"request": request})
        serializer2 = PostListSerializer(post2, context={"request": request})
        serializer3 = PostListSerializer(post3, context={"request": request})

        self.assertIn(serializer1.data, res.data["results"])
        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer3.data, res.data["results"])

    def test_post_like(self):
        post = sample_post(creator=self.user)
        url = reverse("post:post-like-post", args=[post.id])
        request = self.factory.get(url)

        # Like
        res = self.client.post(url)
        count_likes = Post.objects.get(id=post.id).likes.count()
        self.assertEqual(count_likes, 1)

        # Unlike
        res = self.client.post(url)
        count_likes = Post.objects.get(id=post.id).likes.count()
        self.assertEqual(count_likes, 0)

    def test_list_posts_comments(self):
        post = sample_post(creator=self.user)
        sample_comment_for_post(
            post=post,
            writer=self.user,
            content="Comment 1"
        )
        sample_comment_for_post(
            post=post,
            writer=self.user,
            content="Comment 2"
        )

        url = reverse("post:post-comments", args=[post.id])

        request = self.factory.get(url)
        res = self.client.get(url)

        comments = Comment.objects.all()
        serializer = CommentListSerializer(comments, many=True, context={"request": request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_comment_for_post(self):
        post = sample_post(creator=self.user)
        payload = {
            "writer": self.user.id,
            "post": post.id,
            "content": "Some content",
        }
        url = reverse("post:post-comments", args=[post.id])
        request = self.factory.get(url)
        res = self.client.post(url, payload)

        serializer = CommentSerializer(Comment.objects.get(id=1), many=False)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, serializer.data)

    def test_list_of_liked_posts(self):
        post1 = sample_post(
            creator=self.user,
            content="Post 1",
        )
        post2 = sample_post(
            creator=self.user,
            content="Post 2",
        )
        post3 = sample_post(
            creator=self.user,
            content="Post 2",
        )
        _url1 = reverse("post:post-like-post", args=[post1.id])
        _url2 = reverse("post:post-like-post", args=[post2.id])
        self.client.post(_url1)
        self.client.post(_url2)

        url = reverse("post:post-liked-posts")
        request = self.factory.get(url)
        res = self.client.get(url)

        queryset = self.user.liked_posts
        ser1 = PostListSerializer(queryset, many=True, context={"request": request})
        ser3 = PostListSerializer(post3, many=False, context={"request": request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ser1.data, res.data)
        self.assertNotIn(ser3.data, res.data)

    def test_user_posts(self):
        sample_post(
            creator=self.user,
            content="Post 1",
        )
        sample_post(
            creator=self.user,
            content="Post 2",
        )

        url = reverse("post:post-user-posts")
        request = self.factory.get(url)
        res = self.client.get(url)

        queryset = self.user.created_posts
        serializer = PostListSerializer(queryset, many=True, context={"request": request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_followings_posts(self):
        new_user = get_user_model().objects.create_user(
            "new_user@test.com",
            "testpass",
        )
        sample_post(
            creator=new_user,
            content="Post 1",
        )
        sample_post(
            creator=new_user,
            content="Post 2",
        )

        _url = reverse("user:follow", args=[new_user.id])
        self.client.post(_url)

        url = reverse("post:post-followings-posts")
        request = self.factory.get(url)
        res = self.client.get(url)

        following_users = self.user.follows.all()
        queryset = Post.objects.filter(creator__in=following_users)
        serializer = PostListSerializer(queryset, many=True, context={"request": request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    @patch("post.tasks.create_post.apply_async")
    @patch("post.serializers.PostSerializer")
    def test_schedule_creation_post(self, MockPostSerializer, mock_create_post):
        # Mock the serializer
        mock_serializer_instance = MagicMock()
        mock_serializer_instance.is_valid.return_value = True
        MockPostSerializer.return_value = mock_serializer_instance

        # Mock request
        tag = sample_tag()
        data = {
            "title": "Some title",
            "content": "Test content",
            "scheduled_time": "2024-04-06T12:00",
            "tags": [tag.id]
        }
        self.client.force_authenticate(user=self.user)
        url = reverse("post:post-schedule")
        response = self.client.post(url, data, format="json")

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"message": "Post scheduled successfully"})

        # Assert that the create_post task was called with correct arguments
        mock_create_post.assert_called_once()
