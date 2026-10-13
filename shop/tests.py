from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Order, OrderItem, Product


class StoreFlowTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            name="Test Headphones",
            category="Electronics",
            description="A test product for the store.",
            price=Decimal("1250.00"),
            stock=5,
            emoji="🎧",
        )

    def test_home_page_shows_products(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Headphones")

    def test_product_detail_page(self):
        response = self.client.get(reverse("product_detail", args=[self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "₹")

    def test_add_to_cart_and_update_count(self):
        response = self.client.post(reverse("cart_add", args=[self.product.slug]), {"quantity": "2"})
        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(self.client.session["cart"][self.product.slug], 2)
        response = self.client.get(reverse("cart"))
        self.assertContains(response, "Test Headphones")
        self.assertContains(response, "₹2500.00")

    def test_checkout_requires_login(self):
        response = self.client.get(reverse("checkout"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_checkout_creates_order_and_reduces_stock(self):
        user = User.objects.create_user(username="buyer", password="Strong-password-123", email="buyer@example.com")
        self.client.login(username="buyer", password="Strong-password-123")
        self.client.post(reverse("cart_add", args=[self.product.slug]), {"quantity": "2"})
        response = self.client.post(reverse("checkout"), {
            "full_name": "Test Buyer",
            "email": "buyer@example.com",
            "phone": "9876543210",
            "address": "123 Test Street",
            "city": "Chennai",
            "postal_code": "600001",
            "payment_method": "COD",
        })
        self.assertEqual(response.status_code, 302)
        order = Order.objects.get(user=user)
        self.assertEqual(order.total, Decimal("2500.00"))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(OrderItem.objects.get(order=order).quantity, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)
        self.assertEqual(self.client.session["cart"], {})
