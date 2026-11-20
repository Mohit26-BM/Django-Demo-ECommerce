from django.db import migrations


def fix_icon(apps, schema_editor):
    Category = apps.get_model("shop", "Category")
    Category.objects.filter(icon="bi-boot").update(icon="bi-person-walking")


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_product_fields_banner_category_image"),
    ]

    operations = [
        migrations.RunPython(fix_icon, migrations.RunPython.noop),
    ]
