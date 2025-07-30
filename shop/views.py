from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q


from .models import Product, Category


# Reusable category context
def get_categories():
    return Category.objects.all()


def home(request):
    categories = get_categories()
    return render(request, "shop/home.html", {"categories": categories})


def category_products(request, slug):
    categories = get_categories()
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    return render(
        request,
        "shop/category_products.html",
        {
            "categories": categories,
            "category": category,
            "products": products,
        },
    )


def product_detail(request, pk):
    categories = get_categories()
    product = get_object_or_404(Product, pk=pk)
    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
            "categories": categories,
        },
    )


@login_required
def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session["cart"] = cart
    return HttpResponseRedirect(reverse("cart"))


@login_required
def view_cart(request):
    categories = get_categories()
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        item_total = product.price * quantity
        total += item_total
        cart_items.append(
            {"product": product, "quantity": quantity, "item_total": item_total}
        )

    return render(
        request,
        "shop/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
            "categories": categories,
        },
    )


@login_required
@require_POST
def update_cart(request, product_id):
    quantity = int(request.POST.get("quantity", 1))
    cart = request.session.get("cart", {})

    if quantity > 0:
        cart[str(product_id)] = quantity
    else:
        cart.pop(str(product_id), None)

    request.session["cart"] = cart
    return HttpResponseRedirect(reverse("cart"))


@login_required
@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return HttpResponseRedirect(reverse("cart"))


@login_required
def checkout(request):
    categories = get_categories()
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        item_total = product.price * quantity
        total += item_total
        cart_items.append(
            {"product": product, "quantity": quantity, "item_total": item_total}
        )

    if request.method == "POST":
        request.session["cart"] = {}  # Clear cart
        return render(request, "shop/checkout_success.html", {"categories": categories})

    return render(
        request,
        "shop/checkout.html",
        {
            "categories": categories,
            "cart_items": cart_items,
            "total": total,
        },
    )


def search(request):
    query = request.GET.get("q", "")
    categories = get_categories()

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.none()

    return render(
        request,
        "shop/search_results.html",
        {
            "products": products,
            "query": query,
            "categories": categories,
        },
    )


def signup_view(request):
    categories = get_categories()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful. You are now logged in.")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(
        request,
        "registration/signup.html",
        {
            "form": form,
            "categories": categories,
        },
    )


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


def custom_login(request):
    categories = get_categories()
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(
        request,
        "registration/login.html",
        {
            "form": form,
            "categories": categories,
        },
    )
