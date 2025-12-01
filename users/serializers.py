from rest_framework import serializers
from .models import User, SellerAbout

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class SellerAboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerAbout
        fields = '__all__'
