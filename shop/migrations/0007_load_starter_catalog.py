import json
from decimal import Decimal
from pathlib import Path

from django.db import migrations

CATALOG = Path(__file__).resolve().parent.parent / "data" / "catalog.json"


def load_catalog(apps, schema_editor):
    """Fill an empty database with the starter catalogue (categories, products, banners).

    Runs as part of `migrate`, so a fresh deploy always has something to show, with no network
    access and no extra build step. It does nothing when the database already has data, so an
    existing store is never touched. Images are the files already committed under media/.
    """
    Category = apps.get_model("shop", "Category")
    Product = apps.get_model("shop", "Product")
    Banner = apps.get_model("shop", "Banner")

    if Category.objects.exists() or Product.objects.exists():
        return
    if not CATALOG.is_file():
        return

    data = json.loads(CATALOG.read_text(encoding="utf-8"))

    by_slug = {}
    for c in data["categories"]:
        by_slug[c["slug"]] = Category.objects.create(name=c["name"], slug=c["slug"], icon=c["icon"])

    Product.objects.bulk_create([
        Product(
            category=by_slug[p["category"]],
            name=p["name"],
            price=Decimal(p["price"]),
            original_price=Decimal(p["original_price"]) if p["original_price"] is not None else None,
            description=p["description"],
            rating=Decimal(p["rating"]),
            review_count=p["review_count"],
            is_featured=p["is_featured"],
            is_active=p["is_active"],
            image=p["image"],
        )
        for p in data["products"]
    ])

    if not Banner.objects.exists():
        Banner.objects.bulk_create([Banner(**b) for b in data["banners"]])


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0006_fix_shoe_category_icon"),
    ]

    operations = [
        migrations.RunPython(load_catalog, migrations.RunPython.noop),
    ]
