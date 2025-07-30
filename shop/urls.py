from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.custom_login, name="login"),  # Added custom login
    path("logout/", views.logout_view, name="logout"),  # Added logout
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path(
        "cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"
    ),
    path("search/", views.search, name="search"),
]
