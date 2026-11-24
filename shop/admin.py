from django.contrib import admin
from .models import Category
from .models import Order, OrderItem

admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)