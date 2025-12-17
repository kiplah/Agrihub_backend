from django.db import models
from django.conf import settings

class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    imagepath = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories', null=True, blank=True)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name

class Product(models.Model):
    # Core Fields
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    imagepath = models.ImageField(upload_to='products/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    price = models.BigIntegerField()
    
    # New Required Fields
    variety = models.CharField(max_length=255, blank=True, null=True)
    breed = models.CharField(max_length=255, blank=True, null=True)
    quantity_available = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True) # e.g. Kg, Bag, Piece
    location = models.CharField(max_length=255, blank=True, null=True)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    delivery_options = models.CharField(max_length=255, blank=True, null=True)
    
    # Optional Fields
    moisture_content = models.CharField(max_length=50, blank=True, null=True)
    age = models.CharField(max_length=50, blank=True, null=True) # for livestock
    weight = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True) # for inputs
    packaging_size = models.CharField(max_length=100, blank=True, null=True)
    
    # Deprecated but kept for temporary compatibility if needed (can be removed later)
    # category_name = models.CharField(max_length=255, blank=True, null=True) 

    # Analytics & Inventory
    views = models.IntegerField(default=0)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending Approval'),
        ('rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    low_stock_threshold = models.IntegerField(default=10)
    stock_quantity = models.IntegerField(default=0)
    expiry_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
