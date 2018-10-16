from django.db import models
from django.contrib.auth.models import User
from django.db.models import ObjectDoesNotExist

# Create your models here.

# Defines a pizza customers can order
class Pizza(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(default="")
    price = models.FloatField(default=0)
    image_link = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Defines a cart that holds a user selection
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)

    def total(self):
        cart_lines = self.lines.all()
        total = 0
        for line in cart_lines:
            total += line.total()
        return round(total, 2)
    
    def add(self, pizza_id, quantity):
        pizza = Product.objects.get(id=product_id)
        cart_line = Cart_line(cart=self, pizza=pizza, quantity=quantity)
        cart_line.save()


# Defines a line of a cart, holding product, quantity and toppings information
class Cart_line(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="lines")
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=1)

    def total(self):
        return round(self.pizza.price * self.quantity, 2)
    
    def add(self, quantity):
        self.quantity += quantity
        self.save()

# Defines an order
class Order(models.Model):
    date = models.DateTimeField(auto_now=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    def total(self):
        return round(self.cart.total(), 2)
