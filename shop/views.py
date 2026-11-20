from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Order, OrderItem, Product, Category, Wishlist, Banner
from .utils import (
    build_cart_items,
    clamp_quantity,
    clean_cart,
    clear_login_failures,
    login_blocked,
    record_login_failure,
    safe_next_url,
)


def home(request):
    from django.db.models import Count
    banners = Banner.objects.filter(is_active=True)
    featured = (
        Product.objects.filter(is_featured=True, is_active=True)
        .select_related("category")[:8]
    )
    deals = (
        Product.objects.filter(is_active=True, original_price__isnull=False)
        .select_related("category")
        .order_by("-review_count")[:10]
    )
    # Build dynamic per-category sections (top 8 categories by product count)
    top_cats = (
        Category.objects.annotate(product_count=Count("product"))
        .filter(product_count__gt=0)
        .order_by("-product_count")[:8]
    )
    category_sections = []
    for cat in top_cats:
        products = (
            Product.objects.filter(category=cat, is_active=True)
            .select_related("category")
            .order_by("-review_count")[:8]
        )
        if products.exists():
            category_sections.append({"category": cat, "products": products})

    return render(request, "shop/home.html", {
        "banners": banners,
        "featured": featured,
        "deals": deals,
        "category_sections": category_sections,
    })


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True).select_related("category")
    return render(request, "shop/category_products.html", {
        "category": category,
        "products": products,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    related_products = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=pk)
        .select_related("category")[:4]
    )
    return render(request, "shop/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })


def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).select_related("category")
    active_category = None
    sort = request.GET.get("sort", "")

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("id")

    return render(request, "shop/product_list.html", {
        "products": products,
        "categories": categories,
        "active_category": active_category,
        "sort": sort,
    })


def _back_or_cart(request):
    """Return to the page the user came from if it is on this site, else to the cart."""
    ref = request.META.get("HTTP_REFERER", "")
    if ref and url_has_allowed_host_and_scheme(
        ref, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return HttpResponseRedirect(ref)
    return HttpResponseRedirect(reverse("cart"))


@login_required
@require_POST
def add_to_cart(request, product_id):
    get_object_or_404(Product, pk=product_id, is_active=True)
    cart = clean_cart(request.session.get("cart", {}))
    current = cart.get(str(product_id), 0)
    if current >= settings.MAX_CART_QUANTITY:
        messages.info(request, f"You can add at most {settings.MAX_CART_QUANTITY} of one item.")
    else:
        cart[str(product_id)] = current + 1
        messages.success(request, "Item added to cart.")
    request.session["cart"] = cart
    return _back_or_cart(request)


@login_required
def view_cart(request):
    cart_items, total = build_cart_items(request.session.get("cart", {}))
    return render(request, "shop/cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


@login_required
@require_POST
def update_cart(request, product_id):
    quantity = clamp_quantity(request.POST.get("quantity"), default=None)
    cart = clean_cart(request.session.get("cart", {}))
    if quantity is None:
        messages.error(request, "Please enter a valid quantity.")
    elif quantity > 0:
        get_object_or_404(Product, pk=product_id, is_active=True)
        cart[str(product_id)] = quantity
    else:
        cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return HttpResponseRedirect(reverse("cart"))


@login_required
@require_POST
def remove_from_cart(request, product_id):
    cart = clean_cart(request.session.get("cart", {}))
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return HttpResponseRedirect(reverse("cart"))


@login_required
def checkout(request):
    cart_items, total = build_cart_items(request.session.get("cart", {}))

    if request.method == "POST":
        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        payment_method = request.POST.get("payment_method", "COD")
        if payment_method not in ["COD", "UPI", "CARD"]:
            payment_method = "COD"

        # All or nothing: an order never exists without its items.
        with transaction.atomic():
            order = Order.objects.create(user=request.user, total=total, payment_method=payment_method)
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item["product"],
                    quantity=item["quantity"],
                    price=item["product"].price,
                )
                for item in cart_items
            ])
        request.session["cart"] = {}
        messages.success(request, f"Order #{order.id} placed successfully!")
        return render(request, "shop/checkout_success.html", {"order": order})

    return render(request, "shop/checkout.html", {
        "cart_items": cart_items,
        "total": total,
    })


def search(request):
    query = request.GET.get("q", "").strip()
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query), is_active=True
        ).select_related("category")

    return render(request, "shop/search_results.html", {
        "products": products,
        "query": query,
    })


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect(safe_next_url(request, reverse("home")))
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form, "next": safe_next_url(request, "")})


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(safe_next_url(request, reverse("home")))
    if request.method == "POST":
        username = request.POST.get("username", "")
        if login_blocked(request, username):
            messages.error(request, "Too many failed attempts. Please wait a few minutes and try again.")
            form = AuthenticationForm(request)
        else:
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                clear_login_failures(request, username)
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect(safe_next_url(request, reverse("home")))
            record_login_failure(request, username)
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form, "next": safe_next_url(request, "")})


@login_required
def order_history(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )
    return render(request, "shop/order_history.html", {"orders": orders})


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == "Pending":
        order.status = "Cancelled"
        order.save()
        messages.success(request, f"Order #{order.id} has been cancelled.")
    else:
        messages.error(request, "Only pending orders can be cancelled.")
    return redirect("order_history")


@login_required
@require_POST
def request_return(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == "Delivered":
        order.status = "Return Requested"
        order.save()
        messages.success(request, f"Return requested for Order #{order.id}.")
    else:
        messages.error(request, "You can only request a return for delivered orders.")
    return redirect("order_history")


@login_required
@require_POST
def reorder(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = clean_cart(request.session.get("cart", {}))
    added = 0
    for item in order.items.select_related("product"):
        if not item.product.is_active:
            continue
        product_id = str(item.product.id)
        cart[product_id] = min(cart.get(product_id, 0) + item.quantity, settings.MAX_CART_QUANTITY)
        added += 1
    request.session["cart"] = cart
    if added:
        messages.success(request, f"Items from Order #{order.id} added to your cart.")
    else:
        messages.error(request, "None of the items in that order are available any more.")
    return redirect("cart")


@login_required
@require_POST
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status in ["Cancelled", "Delivered", "Return Requested"]:
        order.delete()
        messages.success(request, f"Order #{order_id} removed from your history.")
    else:
        messages.error(request, "You cannot delete an active order.")
    return redirect("order_history")


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    _, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if created:
        messages.success(request, f"{product.name} added to your wishlist.")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    return redirect("wishlist")


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, f"{product.name} removed from your wishlist.")
    return redirect("wishlist")


@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user, product__is_active=True).select_related("product")
    return render(request, "shop/wishlist.html", {"wishlist_items": wishlist_items})
