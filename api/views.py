from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json

class ChatbotView(APIView):
    def post(self, request):
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message required'}, status=status.HTTP_400_BAD_REQUEST)

        ollama_req = {
            "model": "llama3",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an AI assistant for Agro Mart..." # Truncated for brevity, should copy full prompt
                },
                {"role": "user", "content": message}
            ]
        }
        
        try:
            # Using stream=False for simplicity, or handle streaming
            response = requests.post("http://127.0.0.1:11434/api/chat", json=ollama_req, stream=True)
            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = json.loads(line.decode('utf-8'))
                    full_response += decoded_line.get('message', {}).get('content', '')
                    if decoded_line.get('done'):
                        break
            
            return Response({'reply': full_response})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
