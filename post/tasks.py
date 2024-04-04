from celery import shared_task
from django.contrib.auth import get_user_model

from post.models import Post, Tag


@shared_task
def create_post(validated_data, creator_id, tag_ids) -> None:
    creator = get_user_model().objects.get(id=creator_id)
    post = Post.objects.create(creator=creator, **validated_data)
    for tag_id in tag_ids:
        tag = Tag.objects.get(id=tag_id)
        post.tags.add(tag)
    post.save()
    print("Post created successfully!")
