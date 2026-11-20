from decimal import Decimal

from django.conf import settings
from django.core.cache import cache
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Product


def clamp_quantity(value, default=1) -> int:
    """Turn user input into a whole number between 0 and the cart limit."""
    try:
        qty = int(value)
    except (TypeError, ValueError):
        return default
    return max(0, min(qty, settings.MAX_CART_QUANTITY))


def clean_cart(raw) -> dict:
    """Return a cart with only valid 'product id' -> quantity (1..max) entries."""
    cleaned = {}
    if not isinstance(raw, dict):
        return cleaned
    for key, value in raw.items():
        try:
            pid = int(key)
        except (TypeError, ValueError):
            continue
        qty = clamp_quantity(value, default=0)
        if qty > 0:
            cleaned[str(pid)] = qty
    return cleaned


def build_cart_items(cart: dict) -> tuple[list, Decimal]:
    """
    Converts the session cart {product_id: quantity} into a list of
    enriched dicts plus a running total. Products that no longer exist or are
    switched off are dropped, so they can never be bought.
    """
    cart = clean_cart(cart)
    cart_items = []
    total = Decimal("0")
    products_by_id = {
        p.id: p for p in Product.objects.filter(id__in=[int(k) for k in cart], is_active=True)
    }

    for product_id_str, quantity in cart.items():
        product = products_by_id.get(int(product_id_str))
        if product is None:
            continue
        item_total = product.price * quantity
        total += item_total
        cart_items.append({"product": product, "quantity": quantity, "item_total": item_total})

    return cart_items, total


def safe_next_url(request, fallback="/"):
    """The ?next= / next= value if it points at this site, otherwise the fallback."""
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return fallback


def _client_ip(request) -> str:
    return request.META.get("REMOTE_ADDR", "unknown")


def _throttle_key(request, username: str) -> str:
    return f"login-fail:{_client_ip(request)}:{username.lower()[:150]}"


def login_blocked(request, username: str) -> bool:
    return cache.get(_throttle_key(request, username), 0) >= settings.LOGIN_MAX_ATTEMPTS


def record_login_failure(request, username: str) -> None:
    key = _throttle_key(request, username)
    try:
        cache.add(key, 0, settings.LOGIN_ATTEMPT_WINDOW)
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, settings.LOGIN_ATTEMPT_WINDOW)


def clear_login_failures(request, username: str) -> None:
    cache.delete(_throttle_key(request, username))
