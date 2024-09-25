from django.contrib import admin
from .models import Thread, Message

# Register your models here.
@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'created', 'updated')
    filter_horizontal = ('participants',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'thread', 'created', 'is_read')
    list_filter = ('is_read', 'created')
    search_fields = ('text',)