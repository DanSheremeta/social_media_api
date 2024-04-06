from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from post.models import Post, Tag


@shared_task
def create_post(validated_data, creator_id, tag_ids, image_data) -> None:
    creator = get_user_model().objects.get(id=creator_id)
    image = ContentFile(image_data, name="image.png")
    post = Post.objects.create(
        image=image,
        creator=creator,
        **validated_data,
    )
    for tag_id in tag_ids:
        tag = Tag.objects.get(id=tag_id)
        post.tags.add(tag)
    post.save()
