from .models import Product


def build_cart_items(cart: dict) -> tuple[list, float]:
    """
    Converts raw session cart {product_id: quantity} into a list of
    enriched dicts plus a running total. Silently drops any product IDs
    that no longer exist in the database.
    """
    cart_items = []
    total = 0
    ids = [int(pk) for pk in cart.keys()]
    products_by_id = {p.id: p for p in Product.objects.filter(id__in=ids)}

    for product_id_str, quantity in cart.items():
        product = products_by_id.get(int(product_id_str))
        if product is None:
            continue
        item_total = product.price * quantity
        total += item_total
        cart_items.append({
            "product": product,
            "quantity": quantity,
            "item_total": item_total,
        })

    return cart_items, total
