"""
Management command: python manage.py seed_shop

Fetches real products from DummyJSON (https://dummyjson.com), downloads
thumbnail images, and populates the database.

Usage:
  python manage.py seed_shop                   # 100 products
  python manage.py seed_shop --all             # all ~194 products
  python manage.py seed_shop --limit 50        # custom count
  python manage.py seed_shop --keep-banners    # preserve existing banners
"""

import json, os, re, shutil
from urllib.request import urlopen, Request
from urllib.error import URLError

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile

from shop.models import Category, Product, Banner


# Display name and Bootstrap icon for each DummyJSON category slug
CATEGORY_META = {
    "beauty":               {"name": "Beauty",              "icon": "bi-stars"},
    "fragrances":           {"name": "Fragrances",          "icon": "bi-flower1"},
    "furniture":            {"name": "Furniture",           "icon": "bi-house-door"},
    "groceries":            {"name": "Groceries",           "icon": "bi-basket2"},
    "home-decoration":      {"name": "Home Decor",          "icon": "bi-lamp"},
    "kitchen-accessories":  {"name": "Kitchen",             "icon": "bi-cup-hot"},
    "laptops":              {"name": "Laptops",             "icon": "bi-laptop"},
    "mens-shirts":          {"name": "Men's Shirts",        "icon": "bi-person-standing"},
    "mens-shoes":           {"name": "Men's Shoes",         "icon": "bi-boot"},
    "mens-watches":         {"name": "Men's Watches",       "icon": "bi-watch"},
    "mobile-accessories":   {"name": "Mobile Accessories",  "icon": "bi-phone"},
    "motorcycle":           {"name": "Motorcycles",         "icon": "bi-bicycle"},
    "skin-care":            {"name": "Skin Care",           "icon": "bi-droplet"},
    "smartphones":          {"name": "Smartphones",         "icon": "bi-phone-fill"},
    "sports-accessories":   {"name": "Sports",              "icon": "bi-trophy"},
    "sunglasses":           {"name": "Sunglasses",          "icon": "bi-eyeglasses"},
    "tablets":              {"name": "Tablets",             "icon": "bi-tablet"},
    "tops":                 {"name": "Women's Tops",        "icon": "bi-bag"},
    "vehicle":              {"name": "Vehicles",            "icon": "bi-car-front"},
    "womens-bags":          {"name": "Women's Bags",        "icon": "bi-handbag"},
    "womens-dresses":       {"name": "Women's Dresses",     "icon": "bi-heart"},
    "womens-jewellery":     {"name": "Women's Jewellery",   "icon": "bi-gem"},
    "womens-shoes":         {"name": "Women's Shoes",       "icon": "bi-boot"},
    "womens-watches":       {"name": "Women's Watches",     "icon": "bi-smartwatch"},
}


def _fetch_json(url, timeout=15):
    req = Request(url, headers={"User-Agent": "Django/seed_shop"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def to_inr(usd):
    """Convert a USD price to a realistic Indian price point (X99/X49 style)."""
    raw = float(usd) * 83
    if raw < 200:
        bracket = 50
    elif raw < 1000:
        bracket = 100
    elif raw < 5000:
        bracket = 500
    elif raw < 20000:
        bracket = 1000
    else:
        bracket = 5000
    rounded = round(raw / bracket) * bracket
    return min(999999, max(99, int(rounded) - 1))


def _download_image(url, timeout=12):
    """Return a ContentFile for the image at url, or None on failure."""
    try:
        req = Request(url, headers={"User-Agent": "Django/seed_shop"})
        with urlopen(req, timeout=timeout) as resp:
            return ContentFile(resp.read())
    except (URLError, Exception):
        return None


class Command(BaseCommand):
    help = "Seed the store from DummyJSON API (real products + images)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all", action="store_true",
            help="Fetch all available products (~194)",
        )
        parser.add_argument(
            "--limit", type=int, default=100,
            help="Max products to fetch (default: 100, ignored when --all)",
        )
        parser.add_argument(
            "--keep-banners", action="store_true",
            help="Preserve existing banner records and images",
        )
        parser.add_argument(
            "--keep-images", action="store_true",
            help="Reuse already-downloaded product images (skip re-downloading)",
        )

    def handle(self, *args, **options):
        limit = 200 if options["all"] else options["limit"]
        keep_banners = options["keep_banners"]
        keep_images = options["keep_images"]

        # ── Wipe old data ─────────────────────────────────────────────────
        self.stdout.write("Clearing products and categories...")
        Product.objects.all().delete()
        Category.objects.all().delete()
        if not keep_banners:
            Banner.objects.all().delete()

        for subdir in ["products", "categories"]:
            path = os.path.join(settings.MEDIA_ROOT, subdir)
            if not keep_images and os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)

        # ── Fetch from DummyJSON ──────────────────────────────────────────
        self.stdout.write(f"Fetching up to {limit} products from DummyJSON...")
        try:
            data = _fetch_json(
                f"https://dummyjson.com/products?limit={limit}&skip=0"
            )
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"API request failed: {exc}"))
            return

        raw_products = data.get("products", [])
        self.stdout.write(f"  Received {len(raw_products)} products\n")

        # ── Create categories ─────────────────────────────────────────────
        cat_slugs = sorted({p["category"] for p in raw_products})
        cat_map = {}
        for slug in cat_slugs:
            meta = CATEGORY_META.get(slug, {})
            display = meta.get("name") or slug.replace("-", " ").title()
            icon = meta.get("icon", "bi-grid")
            cat = Category.objects.create(name=display, slug=slug, icon=icon)
            cat_map[slug] = cat
            self.stdout.write(f"  [cat] {display}")

        self.stdout.write("")

        # ── Create products ───────────────────────────────────────────────
        created = 0
        featured_count = 0

        for item in raw_products:
            cat = cat_map.get(item["category"])
            if not cat:
                continue

            # Convert USD → INR with realistic price points
            price = to_inr(item["price"])
            discount_pct = float(item.get("discountPercentage") or 0)
            if discount_pct > 0:
                orig = to_inr(item["price"] / (1 - discount_pct / 100))
                original_price = orig if orig != price else None  # drop if both hit the cap
            else:
                original_price = None

            rating = round(min(5.0, float(item.get("rating") or 4.0)), 1)
            stock = int(item.get("stock") or 0)
            review_count = max(10, stock * 18)

            is_featured = (rating >= 4.7 and featured_count < 20)
            if is_featured:
                featured_count += 1

            safe = re.sub(r"[^a-z0-9]+", "-", item["title"].lower())[:50].strip("-")
            filename = f"{safe}-{item['id']}.jpg"
            filepath = os.path.join(settings.MEDIA_ROOT, "products", filename)

            product = Product(
                category=cat,
                name=item["title"],
                price=price,
                original_price=original_price,
                description=item.get("description", ""),
                rating=rating,
                review_count=review_count,
                is_featured=is_featured,
                is_active=True,
            )

            if keep_images and os.path.exists(filepath):
                # Reuse existing file without re-downloading
                product.image = f"products/{filename}"
                product.save()
            else:
                thumbnail_url = item.get("thumbnail", "")
                if thumbnail_url:
                    img = _download_image(thumbnail_url)
                    if img:
                        product.image.save(filename, img, save=False)
                        product.save()
                    else:
                        product.save()
                else:
                    product.save()

            created += 1
            tick = self.style.SUCCESS("[img]") if product.image else "[   ]"
            self.stdout.write(f"  {tick} {item['title']}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Seeded {len(cat_map)} categories and {created} products "
            f"({featured_count} featured).\n"
            f"Banners: {'preserved (--keep-banners)' if keep_banners else 'cleared'}.\n"
        ))
