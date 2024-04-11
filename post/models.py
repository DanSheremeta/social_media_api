import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _


class Comment(models.Model):
    writer = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="comments",
    )
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "created_at",
            "post",
        )

    def __str__(self) -> str:
        return f"{self.writer.username} comment for {self.post.title}"


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.name


def post_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/users/", filename)


class Post(models.Model):
    image = models.ImageField(
        _("post_image"), null=True, upload_to=post_image_file_path
    )
    title = models.CharField(max_length=150)
    content = models.TextField(blank=True)
    creator = models.ForeignKey(
        get_user_model(), related_name="created_posts", on_delete=models.CASCADE
    )
    likes = models.ManyToManyField(
        get_user_model(), related_name="liked_posts", blank=True
    )
    tags = models.ManyToManyField(Tag, verbose_name="tag_posts")
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = (
            "created_at",
            "title",
        )
        verbose_name = "posts"
        verbose_name_plural = "posts"

    @property
    def count_likes(self) -> int:
        """Returns the number of likes on the post."""
        return self.likes.count()

    def __str__(self) -> str:
        return f"{self.creator}: {self.title}"
