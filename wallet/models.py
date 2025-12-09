from django.db import models
from django.conf import settings

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet: {self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'), # Income
        ('debit', 'Debit'),   # Withdrawal/Payment
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='completed') # completed, pending, failed

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} for {self.wallet.user.username}"
