from datetime import datetime, date, time

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.http.response import HttpResponseForbidden
from django.urls import reverse
from django.db.models import Sum
from .models import Pizza, Cart, Cart_line, Order
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.

# Add a pizza to the cart
@login_required(login_url="login")
def add_to_cart(request, pizza_id):
    if request.POST['quantity'] == "0":
        return render(request, "orders/error.html", {"message": "quantity muse be > 0"}, status=400) 
    else:
        quantity = int(request.POST['quantity'])
    # Try to retrieve an existing cart
    try:
        cart = Cart.objects.filter(user=request.user).get(is_ordered=False)
    # If it doesn't exist, create one for the user
    except Cart.DoesNotExist:
        cart = Cart(user=request.user)
        cart.save()
    
    # Get the selected pizza and add to cart
    pizza = Pizza.objects.get(id=pizza_id)
    cart.add(pizza, quantity)
    return redirect("cart")
        
# Delete a line of the cart
@login_required(login_url="login")
def delete_from_cart(request, cart_line_id):
    try:
        Cart_line.objects.get(id=cart_line_id).delete()
    except ObjectDoesNotExist:
        return render(request, "orders/error.html", {"message": "could not delete the Pizza : Pizza does not exist"}, status=404) 
    return redirect("cart")

# Allows a user to order the selection in the cart
@login_required(login_url="login")
def order_cart(request):
    # Get the actuel non-ordered yet cart of the user
    cart = Cart.objects.filter(user=request.user).get(is_ordered=False)
    # Create an order with that cart
    order = Order(cart=cart)
    # Set that particular cart to "ordered"
    cart.is_ordered=True
    order.save()
    cart.save()

    return redirect('cart')

# Allows user to browse their cart
@login_required(login_url="login")
@require_http_methods(['GET', 'POST'])
def cart(request):
    # Get the user's cart, if it doesn't exist, create it
    try:
        cart = Cart.objects.filter(user=request.user).get(is_ordered=False)
    except Cart.DoesNotExist:
        cart = Cart(user=request.user)
        cart.save()

    if request.method == "POST":
        try:
            cart.add(request.POST['pizza_id'], 1)
            cart.save()
            return JsonResponse({"message": "success"})
        except Cart.error:
            return JsonResponse({"message": "error"})
        
    else:
        cart_lines = cart.lines.all()
        cart_total = cart.total()
        context = {
            "cart_lines": cart_lines,
            "cart_total": cart_total
        }
        return render(request, "orders/cart.html", context)

# View the menu
@login_required(login_url="login")
@ensure_csrf_cookie
def index(request):
    # Get pizza
    context = {
        "pizzas": Pizza.objects.all()
    }
    return render(request, "orders/index.html", context)

# Allows users to login
def login_user(request):
    if request.method == "POST":
        if request.POST["username"] == "":
            return render(request, "orders/error.html", {"message": "must provide a username"})
        if request.POST["password"] == "":
            return render(request, "orders/error.html", {"message": "must provide a password"})
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "orders/error.html", {"message": "bad username and/or password"}, status=401)
    else:
        return render(request, "orders/login.html")

# Allows user to logout
def logout_user(request):
    logout(request)
    return render(request, "orders/login.html")

# Allows users to browse their last orders
@login_required(login_url="login")
def orders(request):
    orders = Order.objects.filter(cart__user=request.user)
    context = {
        "orders": orders
    }
    return render(request, "orders/orders.html", context)

# Allows the staff to browse all orders
@staff_member_required
def dashboard(request):
    # Get all orders and count them
    orders = Order.objects.all().order_by('-date')
    orders_count = orders.count()

    # Compute the mean amount of all orders
    orders_mean = 0
    for order in orders:
        orders_mean += order.total()
    orders_mean /= orders_count
    
    # Get the orders of the day
    today_min = datetime.combine(datetime.today(), time.min)
    today_max = datetime.combine(datetime.today(), time.max)
    orders_today = Order.objects.filter(date__range=(today_min, today_max)).count()

    context = {
        "orders": orders,
        "orders_today": orders_today,
        "orders_count": orders_count,
        "orders_mean": orders_mean
    }
    return render(request, "orders/dashboard.html", context)

# Allows users to see details of one order
def order(request, order_id):
    order = Order.objects.get(id=order_id) 
    if request.user.is_staff or (request.user.is_authenticated and request.user == order.cart.user):
        context = {
            "order": order,
            "order_lines": order.cart.lines.all(),
            "order_total": order.total()
        }
        return render(request, "orders/order.html", context)
    else:
        return render(request, "orders/error.html", {"message": "access is forbidden"}, 403)

# Allows users to register
def register(request):
    if request.method == "POST":
        if request.POST["username"] == "":
            return render(request, "orders/error.html", {"message": "must provide a username"})
        if request.POST["password"] == "":
            return render(request, "orders/error.html", {"message": "must provide a password"})
        if request.POST["confirm"] != request.POST["password"]:
            return render(request, "orders/error.html", {"message": "Pasword and confirmation don't match"})
        user = User.objects.create_user(request.POST["username"], "", request.POST["password"])
        user.save()
        return render(request, "orders/login.html")
    else:
        return render(request, "orders/register.html")
