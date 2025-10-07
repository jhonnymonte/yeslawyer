from rest_framework import serializers
from .models import Prompt

class PromptCreateSerializer(serializers.ModelSerializer):
    websocket = serializers.BooleanField(required = False, default = False)
    
    class Meta:
        model = Prompt
        fields =  ["prompt", "websocket"]
        
    def validate_prompt(self,value):
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("prompt to short")
        return value
    

class PromptResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ["id", "prompt", "response", "created_at"]