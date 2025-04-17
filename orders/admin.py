# myproject/orders/admin.py

from django.contrib import admin
from .models import Product, Order, Payment, OrderItem

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(OrderItem)
