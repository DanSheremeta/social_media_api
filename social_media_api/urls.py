from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include("user.urls", namespace="user")),
    path("post/", include("post.urls", namespace="post")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
