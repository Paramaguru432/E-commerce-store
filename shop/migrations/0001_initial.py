# Initial migration for the shop application.
import decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=160)),
                ("slug", models.SlugField(blank=True, max_length=180, unique=True)),
                ("category", models.CharField(choices=[("Electronics", "Electronics"), ("Fashion", "Fashion"), ("Home", "Home & Living"), ("Accessories", "Accessories")], default="Accessories", max_length=40)),
                ("description", models.TextField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("stock", models.PositiveIntegerField(default=10)),
                ("emoji", models.CharField(default="📦", help_text="An emoji used as the product artwork.", max_length=12)),
                ("is_active", models.BooleanField(default=True)),
                ("featured", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-featured", "name"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order_number", models.CharField(blank=True, max_length=20, unique=True)),
                ("full_name", models.CharField(max_length=160)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=30)),
                ("address", models.TextField()),
                ("city", models.CharField(max_length=100)),
                ("postal_code", models.CharField(max_length=20)),
                ("payment_method", models.CharField(choices=[("COD", "Cash on delivery")], default="COD", max_length=20)),
                ("status", models.CharField(choices=[("Placed", "Placed"), ("Processing", "Processing"), ("Shipped", "Shipped"), ("Delivered", "Delivered"), ("Cancelled", "Cancelled")], default="Placed", max_length=20)),
                ("total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("product_name", models.CharField(max_length=160)),
                ("unit_price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("quantity", models.PositiveIntegerField()),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="shop.order")),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="order_items", to="shop.product")),
            ],
        ),
    ]
