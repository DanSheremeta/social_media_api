from django.contrib import admin

from post.models import Post, Comment, Tag


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("writer", "post", "content", "created_at")
    list_filter = ("created_at", "post")
    search_fields = ("writer__username", "post__title")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "created_at")
    list_filter = ("created_at", "tags")
    search_fields = ("title", "creator__username")
