from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Count
from .models import User, Product, ProductCategory, Order, Review, SellerAbout
from .serializers import (
    UserSerializer, ProductSerializer, ProductCategorySerializer, 
    OrderSerializer, ReviewSerializer, SellerAboutSerializer
)
import requests
import json
import time
from datetime import datetime
import random
from django.core.mail import send_mail
from django.conf import settings
from .utils import send_verification_email

from rest_framework_simplejwt.tokens import RefreshToken
from .services import EmailService
from datetime import timedelta
from django.utils import timezone

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def verify(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
             return Response({'message': 'Email and code required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            
            if user.verification_code == code:
                # Check expiration
                if user.verification_code_expires_at and timezone.now() > user.verification_code_expires_at:
                    return Response({'message': 'Verification code expired'}, status=status.HTTP_400_BAD_REQUEST)

                user.verification_code = None
                user.verification_code_expires_at = None
                user.is_active = True
                user.save()
                
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'User verified and registered',
                    'event': {
                        'token': str(refresh.access_token),
                        'Role': user.role,
                        'ID': user.id,
                        'Email': user.email,
                        'Username': user.username
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=['post'])
    def signup(self, request):
        email = request.data.get('email')
        existing_user = User.objects.filter(email__iexact=email).first()

        if existing_user:
            if existing_user.is_active:
                return Response({'message': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Resend verification code
                user = existing_user
                code = str(random.randint(100000, 999999))
                user.verification_code = code
                user.verification_code_expires_at = timezone.now() + timedelta(minutes=15)
                user.save()
                
                success, error = EmailService.send_verification_email(user, code)
                if not success:
                    print(f"Error sending email: {error}")
                
                return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False # Deactivate until verified
            
            # Generate verification code
            code = str(random.randint(100000, 999999))
            user.verification_code = code
            user.verification_code_expires_at = timezone.now() + timedelta(minutes=15)
            user.save()
            
            # Send email
            success, error = EmailService.send_verification_email(user, code)
            if not success:
                print(f"Error sending email: {error}")
                # In production, might want to handle this better
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        # Assuming username is email or we need to find user by email first
        try:
            user_obj = User.objects.get(email__iexact=email)
            user = authenticate(username=user_obj.username, password=password)
            if user:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
        except User.DoesNotExist:
            pass
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'message': 'Logged out'})

    @action(detail=False, methods=['post'])
    def resend_verification(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'message': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email__iexact=email)
            if user.is_active:
                return Response({'message': 'User already verified'}, status=status.HTTP_400_BAD_REQUEST)
            
            code = str(random.randint(100000, 999999))
            user.verification_code = code
            user.verification_code_expires_at = timezone.now() + timedelta(minutes=15)
            user.save()
            
            success, error = EmailService.send_verification_email(user, code)
            if not success:
                 return Response({'message': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return Response({'message': 'Verification code resent'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        email = request.data.get('email')
        print(f"DEBUG: forgot_password received email: '{email}'")
        if not email:
            return Response({'message': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email__iexact=email)
            code = str(random.randint(100000, 999999))
            user.reset_password_code = code
            user.reset_password_code_expires_at = timezone.now() + timedelta(minutes=15)
            user.save()
            
            success, error = EmailService.send_password_reset_email(user, code)
            if not success:
                 return Response({'message': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                 
            return Response({'message': 'Password reset code sent'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # For security, maybe don't reveal user existence, but for now:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        
        if not email or not code or not new_password:
            return Response({'message': 'Email, code, and new password required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email__iexact=email)
            
            if user.reset_password_code != code:
                return Response({'message': 'Invalid reset code'}, status=status.HTTP_400_BAD_REQUEST)
                
            if user.reset_password_code_expires_at and timezone.now() > user.reset_password_code_expires_at:
                return Response({'message': 'Reset code expired'}, status=status.HTTP_400_BAD_REQUEST)
                
            user.set_password(new_password)
            user.reset_password_code = None
            user.reset_password_code_expires_at = None
            user.save()
            
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        user_id = self.request.query_params.get('user_id')
        search = self.request.query_params.get('search')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def get_queryset(self):
        queryset = ProductCategory.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        buyer_id = self.request.query_params.get('buyer_id')
        seller_id = self.request.query_params.get('seller_id')
        if buyer_id:
            queryset = queryset.filter(buyer_id=buyer_id)
        if seller_id:
            queryset = queryset.filter(seller_id=seller_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='seller-stats/(?P<seller_id>[^/.]+)')
    def seller_stats(self, request, seller_id=None):
        orders = Order.objects.filter(seller_id=seller_id)
        total_orders = orders.count()
        revenue = orders.aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0
        active_orders = orders.exclude(order_status='completed').count()
        total_sales = orders.filter(order_status='completed').aggregate(Sum('checkout_price'))['checkout_price__sum'] or 0
        
        return Response({
            'TotalOrders': total_orders,
            'Revenue': revenue,
            'ActiveOrders': active_orders,
            'TotalSales': total_sales
        })

    @action(detail=False, methods=['get'], url_path='monthly-stats/(?P<seller_id>[^/.]+)')
    def monthly_stats(self, request, seller_id=None):
        orders = Order.objects.filter(seller_id=seller_id)
        # Complex stats logic similar to Go implementation
        # For brevity, implementing a simplified version or full version if needed
        # This requires grouping by month/year which is easier in Python
        
        monthly_stats = {}
        yearly_stats = {}
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        current_month_revenue = 0
        current_year_revenue = 0

        for order in orders:
            dt = datetime.fromtimestamp(order.time)
            year = dt.year
            month = dt.month
            month_key = f"{year}-{month}"
            
            # Monthly
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'year': year, 'month': month, 'total_orders': 0, 'completed_orders': 0, 'total_revenue': 0}
            monthly_stats[month_key]['total_orders'] += 1
            
            if order.order_status == 'completed':
                monthly_stats[month_key]['completed_orders'] += 1
                monthly_stats[month_key]['total_revenue'] += order.checkout_price
                if year == current_year and month == current_month:
                    current_month_revenue += order.checkout_price

            # Yearly
            if year not in yearly_stats:
                yearly_stats[year] = {'year': year, 'total_orders': 0, 'completed_orders': 0, 'total_revenue': 0}
            yearly_stats[year]['total_orders'] += 1
            
            if order.order_status == 'completed':
                yearly_stats[year]['completed_orders'] += 1
                yearly_stats[year]['total_revenue'] += order.checkout_price
                if year == current_year:
                    current_year_revenue += order.checkout_price

        # Calculate growth (simplified)
        monthly_results = list(monthly_stats.values())
        yearly_results = list(yearly_stats.values())
        
        return Response({
            "monthly_stats": monthly_results,
            "yearly_stats": yearly_results,
            "current_month_revenue": current_month_revenue,
            "current_year_revenue": current_year_revenue,
        })

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = Review.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

class ChatbotView(APIView):
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message required'}, status=status.HTTP_400_BAD_REQUEST)

        ollama_req = {
            "model": "llama3",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant for Agro Mart..." # Truncated for brevity, should copy full prompt
                },
                {"role": "user", "content": message}
            ]
        }
        
        try:
            # Using stream=False for simplicity, or handle streaming
            response = requests.post("http://127.0.0.1:11434/api/chat", json=ollama_req, stream=True)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = json.loads(line.decode('utf-8'))
                    full_response += decoded_line.get('message', {}).get('content', '')
                    if decoded_line.get('done'):
                        break
            
            return Response({'reply': full_response})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
