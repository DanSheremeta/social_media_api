from rest_framework.permissions import SAFE_METHODS, BasePermission

from post.models import Comment, Post


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsPostCreatorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS", "POST"):
            return True
        return obj.creator == request.user


class IsCommentWriterOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS", "POST"):
            return True
        return obj.writer == request.user
