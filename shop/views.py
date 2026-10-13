from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm, RegisterForm
from .models import Order, OrderItem, Product


def home(request):
    products = Product.objects.filter(is_active=True)
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    valid_categories = {choice[0] for choice in Product.CATEGORY_CHOICES}
    if category in valid_categories:
        products = products.filter(category=category)
    context = {
        "products": products,
        "query": query,
        "selected_category": category,
        "categories": Product.CATEGORY_CHOICES,
        "featured_products": products.filter(featured=True)[:3],
    }
    return render(request, "shop/home.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(is_active=True, category=product.category).exclude(pk=product.pk)[:4]
    return render(request, "shop/product_detail.html", {"product": product, "related_products": related_products})


def _get_cart_items(request):
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict) or not cart:
        return [], Decimal("0.00")
    products = Product.objects.filter(is_active=True, slug__in=list(cart.keys()))
    items = []
    total = Decimal("0.00")
    cleaned_cart = {}
    for product in products:
        try:
            quantity = int(cart.get(product.slug, 0))
        except (TypeError, ValueError):
            continue
        if quantity <= 0:
            continue
        quantity = min(quantity, product.stock)
        if quantity <= 0:
            continue
        line_total = product.price * quantity
        items.append({"product": product, "quantity": quantity, "line_total": line_total})
        total += line_total
        cleaned_cart[product.slug] = quantity
    if cleaned_cart != cart:
        request.session["cart"] = cleaned_cart
    return items, total


def cart(request):
    items, total = _get_cart_items(request)
    return render(request, "shop/cart.html", {"items": items, "total": total})


def cart_add(request, slug):
    if request.method != "POST":
        return redirect("product_detail", slug=slug)
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if product.stock <= 0:
        messages.error(request, "Sorry, this product is currently out of stock.")
        return redirect("product_detail", slug=slug)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, min(quantity, product.stock))
    cart_data = request.session.get("cart", {})
    if not isinstance(cart_data, dict):
        cart_data = {}
    try:
        old_quantity = int(cart_data.get(slug, 0))
    except (TypeError, ValueError):
        old_quantity = 0
    if old_quantity + quantity > product.stock:
        quantity = max(0, product.stock - old_quantity)
    if quantity == 0:
        messages.info(request, f"Your cart already contains the available stock of {product.name}.")
    else:
        cart_data[slug] = old_quantity + quantity
        request.session["cart"] = cart_data
        messages.success(request, f"{product.name} was added to your cart.")
    return redirect("cart")


def cart_update(request, slug):
    if request.method != "POST":
        return redirect("cart")
    product = get_object_or_404(Product, slug=slug, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", "1"))
    except (TypeError, ValueError):
        quantity = 1
    cart_data = request.session.get("cart", {})
    if not isinstance(cart_data, dict):
        cart_data = {}
    if quantity <= 0:
        cart_data.pop(slug, None)
        messages.info(request, f"{product.name} was removed from your cart.")
    elif product.stock <= 0:
        cart_data.pop(slug, None)
        messages.warning(request, f"{product.name} is out of stock and was removed from your cart.")
    else:
        cart_data[slug] = min(quantity, product.stock)
        messages.success(request, "Cart updated.")
    request.session["cart"] = cart_data
    return redirect("cart")


def cart_remove(request, slug):
    if request.method != "POST":
        return redirect("cart")
    cart_data = request.session.get("cart", {})
    if isinstance(cart_data, dict):
        cart_data.pop(slug, None)
        request.session["cart"] = cart_data
    messages.info(request, "Item removed from your cart.")
    return redirect("cart")


@login_required
def checkout(request):
    items, cart_total = _get_cart_items(request)
    if not items:
        messages.info(request, "Your cart is empty. Add a product before checking out.")
        return redirect("home")

    if request.method == "POST":
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            cart_data = request.session.get("cart", {})
            with transaction.atomic():
                products = {
                    p.slug: p
                    for p in Product.objects.select_for_update().filter(
                        is_active=True, slug__in=list(cart_data.keys())
                    )
                }
                if not products or any(slug not in products for slug in cart_data):
                    messages.error(request, "One or more products are no longer available. Please review your cart.")
                    return redirect("cart")

                order_lines = []
                total = Decimal("0.00")
                for slug, raw_quantity in cart_data.items():
                    product = products[slug]
                    try:
                        quantity = int(raw_quantity)
                    except (TypeError, ValueError):
                        quantity = 0
                    if quantity < 1 or quantity > product.stock:
                        messages.error(
                            request,
                            f"Not enough stock for {product.name}. Please update the quantity and try again.",
                        )
                        return redirect("cart")
                    order_lines.append((product, quantity))
                    total += product.price * quantity

                cleaned = form.cleaned_data
                order = Order.objects.create(
                    user=request.user,
                    full_name=cleaned["full_name"],
                    email=cleaned["email"],
                    phone=cleaned["phone"],
                    address=cleaned["address"],
                    city=cleaned["city"],
                    postal_code=cleaned["postal_code"],
                    payment_method=cleaned["payment_method"],
                    total=total,
                )
                for product, quantity in order_lines:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=quantity,
                    )
                    product.stock -= quantity
                    product.save(update_fields=["stock"])

            request.session["cart"] = {}
            messages.success(request, "Your order has been placed successfully!")
            return redirect("order_success", order_number=order.order_number)
    else:
        form = CheckoutForm(user=request.user)

    return render(request, "shop/checkout.html", {"form": form, "items": items, "total": cart_total})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "shop/orders.html", {"orders": orders})


@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_number=order_number, user=request.user)
    return render(request, "shop/order_success.html", {"order": order})


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.save(update_fields=["email"])
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "shop/register.html", {"form": form})
