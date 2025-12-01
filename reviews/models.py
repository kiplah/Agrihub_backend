from django.db import models
from django.conf import settings
from products.models import Product

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # The reviewer
    username = models.CharField(max_length=255) # Redundant if we have user, but keeping for compatibility
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    review = models.TextField()

    def __str__(self):
        return f"Review for {self.product.name} by {self.username}"
