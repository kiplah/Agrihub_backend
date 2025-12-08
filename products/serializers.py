from rest_framework import serializers
from .models import Product, ProductCategory

class ProductCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'imagepath', 'parent', 'subcategories']

    def get_subcategories(self, obj):
        children = obj.subcategories.all()
        return ProductCategorySerializer(children, many=True).data

class ProductSerializer(serializers.ModelSerializer):
    category_details = ProductCategorySerializer(source='category', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'category': {'required': True},
        }
