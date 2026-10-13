from django.core.management.base import BaseCommand
from django.utils.text import slugify

from shop.models import Product


SAMPLE_PRODUCTS = [
    {
        "name": "Cloud Nine Headphones",
        "category": "Electronics",
        "description": "Settle into your favourite playlist with these comfortable everyday headphones. A clean, minimal look and a cosy over-ear feel make them a great desk-to-weekend companion.",
        "price": "2499.00",
        "stock": 18,
        "emoji": "🎧",
        "featured": True,
    },
    {
        "name": "Sunday Ceramic Mug",
        "category": "Home",
        "description": "A sturdy ceramic mug for slow mornings, afternoon tea, and those little pauses in between. Its friendly shape makes every warm drink feel a bit more special.",
        "price": "499.00",
        "stock": 32,
        "emoji": "☕",
        "featured": True,
    },
    {
        "name": "Everywhere Tote Bag",
        "category": "Fashion",
        "description": "A roomy, lightweight tote for books, market finds, and daily essentials. Simple, versatile, and ready to go wherever the day takes you.",
        "price": "799.00",
        "stock": 25,
        "emoji": "👜",
        "featured": True,
    },
    {
        "name": "Pocket Journal Set",
        "category": "Accessories",
        "description": "Keep your plans, quick notes, and bright ideas together with this pocket-sized journal set. A lovely companion for your bag, desk, or bedside table.",
        "price": "349.00",
        "stock": 40,
        "emoji": "📓",
        "featured": False,
    },
    {
        "name": "Soft Knit Cushion",
        "category": "Home",
        "description": "Add a gentle pop of texture to your reading corner or sofa. This soft cushion is designed to make your favourite spot feel even more inviting.",
        "price": "999.00",
        "stock": 14,
        "emoji": "🛋️",
        "featured": False,
    },
    {
        "name": "Daily Active Sneakers",
        "category": "Fashion",
        "description": "A versatile pair for casual outings and busy days. The easy-to-style silhouette pairs with denim, joggers, and your weekend essentials.",
        "price": "1799.00",
        "stock": 12,
        "emoji": "👟",
        "featured": False,
    },
    {
        "name": "Glow Desk Lamp",
        "category": "Electronics",
        "description": "Give your reading or work nook a warm glow with a compact, modern desk lamp. A practical finishing touch for a calmer workspace.",
        "price": "1299.00",
        "stock": 9,
        "emoji": "💡",
        "featured": False,
    },
    {
        "name": "Little Things Keychain",
        "category": "Accessories",
        "description": "A cheerful little detail for your keys or everyday bag. It is lightweight, easy to spot, and a small reminder to enjoy the little things.",
        "price": "199.00",
        "stock": 50,
        "emoji": "🔑",
        "featured": False,
    },
]


class Command(BaseCommand):
    help = "Create the sample products used by the demo storefront. Safe to run repeatedly."

    def handle(self, *args, **options):
        created_count = 0
        for data in SAMPLE_PRODUCTS:
            slug = slugify(data["name"])
            if Product.objects.filter(slug=slug).exists():
                continue
            Product.objects.create(**data, slug=slug, is_active=True)
            created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Sample products ready. Added {created_count} new product(s)."))
