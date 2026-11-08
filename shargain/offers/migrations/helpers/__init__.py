def copy_likes_to_user_offer_states(like_model, state_model, batch_size=500):
    batch = []
    qs = (
        like_model.objects.filter(owner__isnull=False)
        if hasattr(like_model, "objects")
        else like_model.filter(owner__isnull=False)
    )
    for like in qs.iterator(chunk_size=batch_size):
        batch.append(
            state_model(
                user_id=like.owner_id,
                offer_id=like.offer_id,
                liked_at=like.created_at,
            )
        )
        if len(batch) >= batch_size:
            if hasattr(state_model, "objects"):
                state_model.objects.bulk_create(batch, ignore_conflicts=True)
            else:
                state_model.bulk_create(batch, ignore_conflicts=True)
            batch = []
    if batch:
        if hasattr(state_model, "objects"):
            state_model.objects.bulk_create(batch, ignore_conflicts=True)
        else:
            state_model.bulk_create(batch, ignore_conflicts=True)


def copy_user_offer_states_to_likes(state_model, like_model, batch_size=500):
    batch = []
    qs = (
        state_model.objects.filter(liked_at__isnull=False)
        if hasattr(state_model, "objects")
        else state_model.filter(liked_at__isnull=False)
    )
    for state in qs.iterator(chunk_size=batch_size):
        batch.append(
            like_model(
                owner_id=state.user_id,
                offer_id=state.offer_id,
                created_at=state.liked_at,
            )
        )
        if len(batch) >= batch_size:
            if hasattr(like_model, "objects"):
                like_model.objects.bulk_create(batch, ignore_conflicts=True)
            else:
                like_model.bulk_create(batch, ignore_conflicts=True)
            batch = []
    if batch:
        if hasattr(like_model, "objects"):
            like_model.objects.bulk_create(batch, ignore_conflicts=True)
        else:
            like_model.bulk_create(batch, ignore_conflicts=True)
