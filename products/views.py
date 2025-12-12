from rest_framework import viewsets
from .models import Product, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer

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
        
        category = self.request.query_params.get('category')
        if category:
            if category.isdigit():
                queryset = queryset.filter(category__id=category)
            else:
                queryset = queryset.filter(category__name__iexact=category)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer

    def get_queryset(self):
        queryset = ProductCategory.objects.all()
        user_id = self.request.query_params.get('user_id')
        
        if self.action == 'list':
             queryset = queryset.filter(parent__isnull=True)

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset
