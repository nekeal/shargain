from django.utils import timezone

from shargain.offers.migrations.helpers import copy_likes_to_user_offer_states


def test_copy_likes_to_user_offer_states_copies_account_and_ignores_anonymous():
    class DummyLike:
        def __init__(self, owner_id, offer_id, liker_label, created_at):
            self.owner_id = owner_id
            self.offer_id = offer_id
            self.liker_label = liker_label
            self.created_at = created_at

    class DummyLikeQuerySet:
        def __init__(self, items):
            self.items = items

        def filter(self, **kwargs):
            res = self.items
            if kwargs.get("owner__isnull") is False:
                res = [i for i in res if i.owner_id is not None]
            return DummyLikeQuerySet(res)

        def iterator(self, chunk_size=500):
            yield from self.items

    class DummyStateModel:
        def __init__(self):
            self.created = []

        def bulk_create(self, instances, ignore_conflicts=True):
            self.created.extend(instances)

        def __call__(self, user_id, offer_id, liked_at):
            return {"user_id": user_id, "offer_id": offer_id, "liked_at": liked_at}

    now = timezone.now()
    likes = [
        DummyLike(owner_id=1, offer_id=10, liker_label="", created_at=now),
        DummyLike(owner_id=None, offer_id=20, liker_label="anon", created_at=now),
        DummyLike(owner_id=2, offer_id=30, liker_label="", created_at=now),
    ]

    like_model = DummyLikeQuerySet(likes)
    state_model = DummyStateModel()

    copy_likes_to_user_offer_states(like_model, state_model)

    assert len(state_model.created) == 2
    assert state_model.created[0] == {"user_id": 1, "offer_id": 10, "liked_at": now}
    assert state_model.created[1] == {"user_id": 2, "offer_id": 30, "liked_at": now}
