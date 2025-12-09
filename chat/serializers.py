from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    receiver_username = serializers.ReadOnlyField(source='receiver.username')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'receiver', 'receiver_username', 'content', 'timestamp', 'is_read', 'attachment']
        read_only_fields = ['sender', 'timestamp', 'is_read']

    def create(self, validated_data):
        # Allow passing receiver ID needed? 
        # Actually ModelSerializer handles FK usually if passed as ID.
        # But we want to ensure sender is current user usually sets in view.
        return super().create(validated_data)
