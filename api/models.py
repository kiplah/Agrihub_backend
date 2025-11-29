from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role = models.CharField(max_length=50, blank=True, null=True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_expires_at = models.DateTimeField(blank=True, null=True)
    reset_password_code = models.CharField(max_length=6, blank=True, null=True)
    reset_password_code_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.username

class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    imagepath = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    imagepath = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category_name = models.CharField(max_length=255, blank=True, null=True) # Keeping as string to match Go, or could link to ProductCategory
    price = models.BigIntegerField()

    def __str__(self):
        return self.name

class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_orders')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_orders')
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

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # The reviewer
    username = models.CharField(max_length=255) # Redundant if we have user, but keeping for compatibility
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    review = models.TextField()

    def __str__(self):
        return f"Review for {self.product.name} by {self.username}"

class SellerAbout(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_about')
    about = models.TextField()
    product_type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"About {self.user.username}"
