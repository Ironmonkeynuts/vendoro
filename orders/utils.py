from django.db import transaction, IntegrityError
from .models import Cart


def get_active_cart(request, create=True):
    """
    Returns the active cart for the current request.

    Behaviour:
    - Guests:
        * Cart is linked via session_key and cart_id in the session.
    - Logged-in users:
        * If there is a guest cart referenced by cart_id in session, it is
          either claimed (if no user cart exists) or merged into the existing
          user cart (if one exists).
        * Finally, always returns a single active cart for that user.

    If create=False and no cart exists, returns None.
    """
    with transaction.atomic():
        cart = None
        cart_id = request.session.get("cart_id")

        # 1) If we have a cart_id stored in the session, try that first
        if cart_id:
            cart = (
                Cart.objects
                .select_for_update()
                .filter(id=cart_id, active=True)
                .first()
            )
            if not cart:
                # Stale ID
                request.session.pop("cart_id", None)
                cart_id = None

        # 2) Authenticated user branch
        if request.user.is_authenticated:
            # If we have a cart from the session, and it was a guest cart,
            # we need to either claim it
            # or merge it into an existing user cart.
            if cart and cart.user is None:
                # See if this user already has an active cart
                user_cart_qs = (
                    Cart.objects
                    .select_for_update()
                    .filter(user=request.user, active=True)
                    .order_by("-id")
                )
                user_cart = user_cart_qs.first()

                if user_cart and user_cart.pk != cart.pk:
                    # Merge guest cart into existing user cart
                    for g_item in cart.items.all():
                        u_item, created = user_cart.items.get_or_create(
                            product=g_item.product,
                            defaults={"quantity": g_item.quantity},
                        )
                        if not created:
                            u_item.quantity += g_item.quantity
                            u_item.save(update_fields=["quantity"])

                    # Remove the guest cart; user_cart becomes our active cart
                    cart.delete()
                    cart = user_cart
                else:
                    # No existing user cart, just claim this one
                    cart.user = request.user
                    cart.session_key = None
                    cart.save(update_fields=["user", "session_key"])

            elif cart and cart.user != request.user:
                # The cart in session belongs to a different user (!)
                # Ignore it for safety.
                request.session.pop("cart_id", None)
                cart = None

            # If we still don't have a cart, find/create one for this user
            if not cart:
                qs = (
                    Cart.objects
                    .select_for_update()
                    .filter(user=request.user, active=True)
                    .order_by("-id")
                )
                cart = qs.first()
                if cart:
                    # Ensure only one active cart for this user
                    qs.exclude(pk=cart.pk).update(active=False)
                elif create:
                    try:
                        cart = Cart.objects.create(user=request.user, active=True)
                    except IntegrityError:
                        cart = (
                            Cart.objects
                            .select_for_update()
                            .filter(user=request.user, active=True)
                            .order_by("-id")
                            .first()
                        )

            if cart:
                request.session["cart_id"] = cart.id
                request.session.modified = True

            return cart if (cart or create) else None

        # 3) Guest branch (anonymous user)
        if cart and cart.user is not None:
            # Cart in session actually belongs to a user; ignore it as guest
            request.session.pop("cart_id", None)
            cart = None

        if not cart:
            # Ensure we have a session key if we're going to create a cart
            if not request.session.session_key:
                if not create:
                    return None
                request.session.save()
            skey = request.session.session_key

            qs = (
                Cart.objects
                .select_for_update()
                .filter(user__isnull=True, session_key=skey, active=True)
                .order_by("-id")
            )
            cart = qs.first()
            if cart:
                qs.exclude(pk=cart.pk).update(active=False)
            elif create:
                try:
                    cart = Cart.objects.create(
                        user=None,
                        session_key=skey,
                        active=True,
                    )
                except IntegrityError:
                    cart = (
                        Cart.objects
                        .select_for_update()
                        .filter(user__isnull=True, session_key=skey, active=True)
                        .order_by("-id")
                        .first()
                    )

        if cart:
            request.session["cart_id"] = cart.id
            request.session.modified = True

        return cart if (cart or create) else None
