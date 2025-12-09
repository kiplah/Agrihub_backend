from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Message
from .serializers import MessageSerializer

User = get_user_model()

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(receiver=user))

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def conversations(self, request):
        user = request.user
        # unique users derived from messages
        sent_to = Message.objects.filter(sender=user).values_list('receiver', flat=True)
        received_from = Message.objects.filter(receiver=user).values_list('sender', flat=True)
        user_ids = set(sent_to) | set(received_from)
        
        users = User.objects.filter(id__in=user_ids)
        data = [{'id': u.id, 'username': u.username} for u in users]
        return Response(data)

    @action(detail=False, methods=['get'])
    def thread(self, request):
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response({"error": "user_id param required"}, status=400)
            
        user = request.user
        messages = Message.objects.filter(
            (Q(sender=user) & Q(receiver_id=other_user_id)) |
            (Q(sender_id=other_user_id) & Q(receiver=user))
        ).order_by('timestamp')
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
