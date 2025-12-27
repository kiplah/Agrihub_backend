from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    user_name = serializers.CharField(source='buyer.username', read_only=True)
    product_image = serializers.ImageField(source='product.imagepath', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
