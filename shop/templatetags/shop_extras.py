from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


def _group_indian(digits: str) -> str:
    """12345678 -> 1,23,45,678 (Indian digit grouping)."""
    if len(digits) <= 3:
        return digits
    head, tail = digits[:-3], digits[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts) + "," + tail


@register.filter
def inr(value):
    """Format a number as rupees: 124999 -> ₹1,24,999 ; 99.5 -> ₹99.50."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return ""
    amount = amount.quantize(Decimal("0.01"))
    sign = "-" if amount < 0 else ""
    whole, _, frac = f"{abs(amount):.2f}".partition(".")
    text = _group_indian(whole)
    if frac != "00":
        text += "." + frac
    return f"{sign}₹{text}"


@register.simple_tag
def savings(original, price):
    """Rupees saved versus the original price (never negative)."""
    try:
        diff = Decimal(str(original)) - Decimal(str(price))
    except (InvalidOperation, ValueError, TypeError):
        return ""
    return inr(diff) if diff > 0 else ""
