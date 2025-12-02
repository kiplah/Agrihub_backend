from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, SellerAbout
from .serializers import UserSerializer, SellerAboutSerializer
from api.services import EmailService
from datetime import timedelta
from django.utils import timezone
import random
import os

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
        print(f"Signup Validation Errors: {serializer.errors}")
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

class SellerAboutViewSet(viewsets.ModelViewSet):
    queryset = SellerAbout.objects.all()
    serializer_class = SellerAboutSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = SellerAbout.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

class ContactUsView(APIView):
    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        message = request.data.get('message')
        
        if not name or not email or not message:
            return Response({'error': 'Name, email, and message are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Send email to admin
        admin_email = os.getenv("BREVO_FROM_EMAIL") # Send to self/admin
        subject = f"Contact Us Message from {name}"
        content = f"Name: {name}<br>Email: {email}<br>Message:<br>{message}"
        
        success, error = EmailService._send_email(admin_email, subject, content)
        
        if success:
            return Response({'message': 'Message sent successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to send message'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
