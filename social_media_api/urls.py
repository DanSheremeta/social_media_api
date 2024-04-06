from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("api/admin/", admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/post/", include("post.urls", namespace="post")),
    path("api/doc/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
