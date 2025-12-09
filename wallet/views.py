from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        # Ensure wallet exists
        wallet, created = Wallet.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(wallet)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def deposit(self, request):
        # Mock deposit logic for demo
        amount = request.data.get('amount')
        if not amount:
             return Response({"error": "Amount required"}, status=400)
        
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        wallet.balance += float(amount)
        wallet.save()
        
        Transaction.objects.create(
            wallet=wallet, 
            amount=amount, 
            transaction_type='credit', 
            description='Deposit Funds'
        )
        return Response(self.get_serializer(wallet).data)
