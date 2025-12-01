from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SellerAboutViewSet, ContactUsView

router = DefaultRouter()
router.register(r'seller-about', SellerAboutViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/contact-us/', ContactUsView.as_view(), name='contact-us'),
    path('signup/', UserViewSet.as_view({'post': 'signup'}), name='signup'),
    path('verify/', UserViewSet.as_view({'post': 'verify'}), name='verify'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
    path('resend-verification/', UserViewSet.as_view({'post': 'resend_verification'}), name='resend-verification'),
    path('users/forgot_password/', UserViewSet.as_view({'post': 'forgot_password'}), name='forgot-password'),
    path('users/reset_password/', UserViewSet.as_view({'post': 'reset_password'}), name='reset-password'),
]
