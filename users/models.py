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

class SellerAbout(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_about')
    about = models.TextField()
    product_type = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"About {self.user.username}"
