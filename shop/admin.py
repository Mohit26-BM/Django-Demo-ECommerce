from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Wishlist, Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "order")
    list_editable = ("is_active", "order")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "original_price", "rating", "is_featured", "is_active")
    list_filter = ("category", "is_featured", "is_active")
    list_editable = ("is_featured", "is_active")
    search_fields = ("name", "description")
    list_select_related = ("category",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at",)
    inlines = [OrderItemInline]
    list_select_related = ("user",)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "added_at")
    list_select_related = ("user", "product")
    search_fields = ("user__username", "product__name")
