from django.urls import path
from django.urls import path, include
from chat_app.views import (ThreadListCreateView, 
                    ThreadRetrieveUpdateDestroyView, 
                    MessageListCreateView, 
                    MessageRetrieveUpdateDestroyView,
                    MarkMessageAsReadView, 
                    UnreadMessageCountView)

urlpatterns = [  
    # creation (if a thread with particular users exists - just return it.); 
    # removing a thread; 
    # retrieving the list of threads for any user;
    path('threads/', ThreadListCreateView.as_view({'get': 'list', 'post': 'create',}), name='thread-list-create'), 
    path('threads/<int:pk>/', ThreadRetrieveUpdateDestroyView.as_view({'get': 'retrieve', 'post': 'update', 'delete':'destroy'}), name='thread-detail'),

    # creation of a message and retrieving message list for the thread;
    # marking the message as read;
    # retrieving a number of unread messages for the user.
    path('threads/<int:thread_id>/messages/', MessageListCreateView.as_view({'get': 'list', 'post': 'create'}), name='message-list-create'),
    path('threads/<int:thread_id>/messages/<int:pk>/', MessageRetrieveUpdateDestroyView.as_view({'get': 'retrieve', 'post': 'update', 'delete':'destroy'}), name='message-detail'),
    path('threads/<int:thread_id>/messages/<int:pk>/mark_as_read/', MarkMessageAsReadView.as_view({'post': 'update'}), name='mark-message-as-read'),
    path('threads/<int:thread_id>/messages/unread_count/', UnreadMessageCountView.as_view({'get': 'retrieve'}), name='unread-message-count'),
]  
