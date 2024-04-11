from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient, APIRequestFactory
from rest_framework import status

from user.serializers import UserListSerializer


def sample_user(**params):
    defaults = {
        "email": "test@example.com",
        "password": "testpass",
    }
    defaults.update(params)
    return get_user_model().objects.create(**defaults)


class AuthenticatedMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.user = sample_user(username="test_user")
        self.client.force_authenticate(self.user)

    def test_follow_invalid_user(self):
        # Unfollows invalid user
        new_user = sample_user(email="new_user@test.com")
        self.user.follows.add(new_user)
        url = reverse("user:follow", args=[new_user.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data, {"error": "You cannot follow this user."})

        # Unfollows itself
        url = reverse("user:follow", args=[self.user.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data, {"error": "You cannot follow this user."})

    def test_follow_user(self):
        new_user = sample_user(email="new_user@test.com")
        url = reverse("user:follow", args=[new_user.id])
        res = self.client.post(url)

        queryset = self.user.follows.all()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data, {"message": "User followed successfully."})
        self.assertIn(new_user, queryset)

    def test_unfollow_invalid_user(self):
        # Unfollows invalid user
        new_user = sample_user(email="new_user@test.com")
        url = reverse("user:follow", args=[new_user.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data, {"error": "You cannot unfollow this user."})

        # Unfollows itself
        url = reverse("user:follow", args=[self.user.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data, {"error": "You cannot unfollow this user."})

    def test_unfollow_user(self):
        new_user = sample_user(email="new_user@test.com")
        self.user.follows.add(new_user)

        url = reverse("user:follow", args=[new_user.id])
        res = self.client.delete(url)

        queryset = self.user.follows.all()
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(res.data, {"message": "User unfollowed successfully."})
        self.assertNotIn(new_user, queryset)

    def test_users_list_filter_by_username(self):
        user1 = sample_user(email="user1@test.com", username="user1")

        url = reverse("user:list")
        request = self.factory.get(url, {"username": "tes"})
        res = self.client.get(url, {"username": "tes"})

        serializer1 = UserListSerializer(self.user, context={"request": request})
        serializer2 = UserListSerializer(user1, context={"request": request})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])
