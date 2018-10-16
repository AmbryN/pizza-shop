from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cart", views.cart, name="cart"),
    path("cart/add/<int:pizza_id>", views.add_to_cart, name="cart_add"),
    path("cart/delete/<int:cart_line_id>", views.delete_from_cart, name="cart_delete"),
    path("cart/order", views.order_cart, name="cart_order"),
    path("register", views.register, name="register"),
    path("login", views.login_user, name="login"),
    path("logout", views.logout_user, name="logout"),
    path("orders", views.orders, name="orders"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("order/<int:order_id>", views.order, name="order")

]
