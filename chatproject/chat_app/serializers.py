from rest_framework import serializers
from .models import Thread, Message
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ThreadSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Thread
        fields = ['id', 'participants', 'created', 'updated']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    thread = ThreadSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'thread', 'created', 'is_read']
        read_only_fields = ['thread', 'is_read']