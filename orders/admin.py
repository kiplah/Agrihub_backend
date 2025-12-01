from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'product', 'checkout_price', 'order_status', 'time')
    list_filter = ('order_status',)
