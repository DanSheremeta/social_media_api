import os
import uuid

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def user_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.email)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/users/", filename)


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"),
        max_length=100,
        validators=[username_validator],
    )
    avatar = models.ImageField(
        _("avatar"),
        null=True,
        upload_to=user_image_file_path,
    )
    bio = models.TextField(
        _("biography"),
        max_length=255,
        null=True
    )
    birthday = models.DateField(
        _("birthday"),
        null=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ("email",)
        verbose_name = _("user")
        verbose_name_plural = _("users")