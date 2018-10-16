from django.contrib import admin
from .models import Pizza, Cart, Cart_line, Order

# Register your models here.
admin.site.register(Pizza)
admin.site.register(Cart)
admin.site.register(Cart_line)
admin.site.register(Order)