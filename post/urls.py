from django.urls import path, include
from rest_framework import routers

from post.views import TagViewSet, PostViewSet, CommentManageViewSet

router = routers.DefaultRouter()
router.register("tags", TagViewSet)
router.register("comment", CommentManageViewSet)
router.register("", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "post"
