from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.pagination import LimitOffsetPagination

from .models import Thread, Message
from .serializers import ThreadSerializer, MessageSerializer
import datetime

class ThreadListCreateView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer
    #  Provide pagination(LimitOffsetPagination) where it is needed.
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user)

    def create(self, request):
        participant_id = request.data.get('participant_id')
        if not participant_id:
            return Response({"error": "Participant ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            participant = User.objects.get(id=participant_id)
        except User.DoesNotExist:
            return Response({"error": "User with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)

        existing_thread = Thread.objects.filter(participants=request.user).filter(participants=participant).first()
        if existing_thread:
            serializer = self.get_serializer(existing_thread)
            return Response(serializer.data)

        participant = get_object_or_404(User, id=participant_id)
        thread = Thread()
        thread.save()
        thread.participants.add(participant)  
        thread.participants.add(request.user) 
        serializer = self.get_serializer(thread)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
class ThreadRetrieveUpdateDestroyView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ThreadSerializer
    #  Provide pagination(LimitOffsetPagination) where it is needed.
    pagination_class = LimitOffsetPagination
    
    def get_object(self, pk):
        try:
            return Thread.objects.get(pk=pk)
        except Thread.DoesNotExist:
            return None

    def retrieve(self, request, pk=None):
        thread = self.get_object(pk)
        if not thread:
            return Response({'detail': 'Thread not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ThreadSerializer(thread)
        return Response(serializer.data)

    def update(self, request, pk=None):
        thread = self.get_object(pk)
        if not thread:
            return Response({'detail': 'Thread not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ThreadSerializer(thread, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        thread = self.get_object(pk)
        if not thread:
            return Response({'detail': 'Thread not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        thread.delete()
        return Response({'detail': 'Thread deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    
class MessageListCreateView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    #  Provide pagination(LimitOffsetPagination) where it is needed.
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        thread_id = self.kwargs.get('thread_id')
        thread = get_object_or_404(Thread, id=thread_id, participants=self.request.user)
        return Message.objects.filter(thread=thread)

    def perform_create(self, serializer):
        thread_id = self.kwargs.get('thread_id')
        thread = get_object_or_404(Thread, id=thread_id, participants=self.request.user)
        serializer.save(sender=self.request.user, thread=thread)


    
class MessageRetrieveUpdateDestroyView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    #  Provide pagination(LimitOffsetPagination) where it is needed.
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        thread_id = self.kwargs.get('thread_id')
        return Message.objects.filter(thread_id=thread_id)

    def get_object(self):
        queryset = self.get_queryset()
        message_id = self.kwargs.get('pk')
        obj = get_object_or_404(queryset, id=message_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, thread_id, pk=None):
        message = self.get_object()
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    def update(self, request, thread_id, pk=None):
        message = self.get_object()
        
        # Check if the user is the sender of the message
        if message.sender != request.user:
            return Response({"detail": "You don't have permission to edit this message."},
                            status=status.HTTP_403_FORBIDDEN)
        
        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, thread_id, pk=None):
        message = self.get_object()
        
        # Check if the user is the sender of the message
        if message.sender != request.user:
            return Response({"detail": "You don't have permission to delete this message."},
                            status=status.HTTP_403_FORBIDDEN)
        
        message.delete()
        return Response({"message: Your message is successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
    
class MarkMessageAsReadView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    #  Provide pagination(LimitOffsetPagination) where it is needed.
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        thread_id = self.kwargs.get('thread_id')
        return Message.objects.filter(thread_id=thread_id)

    def get_object(self):
        queryset = self.get_queryset()
        message_id = self.kwargs.get('pk')
        obj = get_object_or_404(queryset, id=message_id)
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, thread_id, pk=None):
        message = self.get_object()
        thread = get_object_or_404(Thread, id=thread_id)
        sender = message.sender

        # Check if the user is a participant in the thread
        if request.user not in thread.participants.all():
            return Response({"detail": "You don't have permission to mark this message as read."},
                            status=status.HTTP_403_FORBIDDEN)
        
        # Check if the user is a sender in the thread
        if request.user == sender:
            return Response({"message: This function is not for you. It's for your client."},
                            status=status.HTTP_200_OK)
        # Check if the message is not already read
        if not message.is_read:
            message.is_read = True
            message.save()

        serializer = MessageSerializer(message)
        return Response(serializer.data)
    
class UnreadMessageCountView(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    #  Provide pagination(LimitOffsetPagination) where it is needed.
    pagination_class = LimitOffsetPagination
    
    def retrieve(self, request, thread_id=None):
        # Get the thread or return 404 if not found
        thread = get_object_or_404(Thread, id=thread_id)

        # Check if the user is a participant in the thread
        if request.user not in thread.participants.all():
            return Response(
                {"detail": "You are not a participant in this thread."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Count unread messages for the current user in this thread
        unread_count = Message.objects.filter(thread=thread,is_read=False).exclude(sender=request.user).count()

        # Prepare the response data
        data = {
            "thread_id": thread_id,
            "unread_count": unread_count
        }

        return Response(data, status=status.HTTP_200_OK)