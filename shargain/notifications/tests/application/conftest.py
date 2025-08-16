import pytest
from django.contrib.auth import get_user_model

from shargain.notifications.application.actor import Actor

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def actor(user):
    return Actor(user_id=user.id)
