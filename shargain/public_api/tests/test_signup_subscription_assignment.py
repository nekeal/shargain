import pytest
from django.test import Client

from shargain.accounts.models import CustomUser
from shargain.subscriptions.models import UserSubscription


@pytest.mark.django_db
def test_signup_assigns_free_subscription_and_creates_active_subscription_row():
    client = Client()

    response = client.post(
        "/api/public/auth/signup",
        data={"email": "new-user@example.com", "password": "test-pass-123"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    user = CustomUser.objects.get(email="new-user@example.com")
    active_subscription = UserSubscription.objects.get(user=user, is_active=True)

    assert active_subscription.plan.slug == "free"
    assert active_subscription.expires_at is None
