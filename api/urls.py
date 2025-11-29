from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProductViewSet, CategoryViewSet, 
    OrderViewSet, ReviewViewSet, ChatbotView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'order', OrderViewSet)
router.register(r'review', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/chatbot', ChatbotView.as_view(), name='chatbot'),
    # Custom auth routes if not using ViewSet actions directly or for convenience
    path('signup/', UserViewSet.as_view({'post': 'signup'}), name='signup'),
    path('verify/', UserViewSet.as_view({'post': 'verify'}), name='verify'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
]
