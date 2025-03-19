# tasks/views.py
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import Task
from .serializers import TaskSerializer
from .priority_queue import TaskPriorityQueue

from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Allow anyone to register

# Custom filter set for Task model
class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = {
            'status': ['exact'],
            'priority': ['exact'],
            'created_at': ['gte', 'lte']
        }

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TaskFilter
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return tasks belonging to the current user only"""
        return Task.objects.filter(user=self.request.user)
    
    # Cache list view for improved performance
    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Ensure the user is set on task creation"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        """Return tasks sorted by priority queue algorithm"""
        # Get user's tasks
        tasks = self.get_queryset()
        
        # Initialize priority queue
        pq = TaskPriorityQueue()
        
        # Add all tasks to the queue
        for task in tasks:
            pq.add_task(task)
        
        # Get all tasks in priority order
        prioritized_tasks = pq.get_all_sorted()
        
        # Apply pagination
        page = self.paginate_queryset(prioritized_tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(prioritized_tasks, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Return statistics about user's tasks"""
        tasks = self.get_queryset()
        stats = {
            'total_tasks': tasks.count(),
            'pending_tasks': tasks.filter(status='pending').count(),
            'completed_tasks': tasks.filter(status='completed').count(),
            'high_priority': tasks.filter(priority='high').count(),
            'medium_priority': tasks.filter(priority='medium').count(),
            'low_priority': tasks.filter(priority='low').count(),
        }
        return Response(stats)
        
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed"""
        task = self.get_object()
        task.status = Task.Status.COMPLETED
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)
        
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Mark a completed task as pending"""
        task = self.get_object()
        if task.status != Task.Status.COMPLETED:
            raise ValidationError({"status": "Task is not completed"})
        task.status = Task.Status.PENDING
        task.save()
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def clear_completed(self, request):
        """Delete all completed tasks"""
        count = self.get_queryset().filter(status=Task.Status.COMPLETED).delete()[0]
        return Response({"message": f"Deleted {count} completed tasks"}, status=status.HTTP_204_NO_CONTENT)