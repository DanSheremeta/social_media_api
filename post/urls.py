from django.urls import path, include
from rest_framework import routers

from post.views import TagViewSet, PostViewSet

router = routers.DefaultRouter()
router.register("tags", TagViewSet)
router.register("", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "post"
