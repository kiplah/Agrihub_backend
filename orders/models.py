from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_orders')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    shipping_address = models.TextField()
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.BigIntegerField()
    phone_number = models.BigIntegerField()
    delivery_option = models.CharField(max_length=100)
    checkout_price = models.BigIntegerField()
    order_status = models.CharField(max_length=50, default='pending')
    payment_method = models.CharField(max_length=50)
    time = models.BigIntegerField() # Unix timestamp

    def __str__(self):
        return f"Order {self.id} by {self.buyer.username}"
