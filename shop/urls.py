from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="product_list"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("category/<slug:slug>/", views.category_products, name="category_products"),

    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="cart"),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),

    path("checkout/", views.checkout, name="checkout"),

    path("search/", views.search, name="search"),

    path("signup/", views.signup_view, name="signup"),
    path("login/", views.custom_login, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("orders/", views.order_history, name="order_history"),
    path("orders/cancel/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("orders/return/<int:order_id>/", views.request_return, name="request_return"),
    path("orders/reorder/<int:order_id>/", views.reorder, name="reorder"),
    path("orders/delete/<int:order_id>/", views.delete_order, name="delete_order"),

    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("wishlist/remove/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
]
