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
    user = serializers.ReadOnlyField(source='user.username')
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    category_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'category': {'required': False},
        }

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)
        product = Product.objects.create(**validated_data)
        
        if category_name:
            category, _ = ProductCategory.objects.get_or_create(name=category_name)
            product.category = category
            product.save()
            
        return product
