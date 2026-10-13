from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<slug:slug>/", views.cart_add, name="cart_add"),
    path("cart/update/<slug:slug>/", views.cart_update, name="cart_update"),
    path("cart/remove/<slug:slug>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<str:order_number>/", views.order_success, name="order_success"),
    path("register/", views.register, name="register"),
]
