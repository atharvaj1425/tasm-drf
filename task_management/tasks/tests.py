from django.test import TestCase

# Create your tests here.
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]

# Step 10: Unit Tests
# tasks/tests.py
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Task

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def make_user(**kwargs):
        return User.objects.create_user(
            username=kwargs.get('username', 'testuser'),
            password=kwargs.get('password', 'password123')
        )
    return make_user

@pytest.fixture
def authenticated_client(api_client, create_user):
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user

@pytest.mark.django_db
def test_create_task(authenticated_client):
    client, user = authenticated_client
    task_data = {
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 'high',
        'status': 'pending'
    }
    
    url = reverse('task-list')
    response = client.post(url, task_data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Task.objects.count() == 1
    assert Task.objects.get().title == 'Test Task'
    assert Task.objects.get().user == user

@pytest.mark.django_db
def test_get_task_list(authenticated_client):
    client, user = authenticated_client
    
    # Create some tasks
    Task.objects.create(title='Task 1', user=user)
    Task.objects.create(title='Task 2', user=user)
    
    url = reverse('task-list')
    response = client.get(url, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2

@pytest.mark.django_db
def test_update_task(authenticated_client):
    client, user = authenticated_client
    
    # Create a task
    task = Task.objects.create(title='Original Title', user=user)
    
    url = reverse('task-detail', kwargs={'pk': task.pk})
    response = client.patch(url, {'title': 'Updated Title'}, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    task.refresh_from_db()
    assert task.title == 'Updated Title'

@pytest.mark.django_db
def test_delete_task(authenticated_client):
    client, user = authenticated_client
    
    # Create a task
    task = Task.objects.create(title='Task to Delete', user=user)
    
    url = reverse('task-detail', kwargs={'pk': task.pk})
    response = client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Task.objects.count() == 0

@pytest.mark.django_db
def test_task_filter_by_priority(authenticated_client):
    client, user = authenticated_client
    
    # Create tasks with different priorities
    Task.objects.create(title='High Task', priority='high', user=user)
    Task.objects.create(title='Medium Task', priority='medium', user=user)
    Task.objects.create(title='Low Task', priority='low', user=user)
    
    url = reverse('task-list') + '?priority=high'
    response = client.get(url, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == 'High Task'

@pytest.mark.django_db
def test_scheduled_endpoint(authenticated_client):
    client, user = authenticated_client
    
    # Create tasks with different priorities
    Task.objects.create(title='High Task', priority='high', user=user)
    Task.objects.create(title='Medium Task', priority='medium', user=user)
    Task.objects.create(title='Low Task', priority='low', user=user)
    
    url = reverse('task-scheduled')
    response = client.get(url, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 3
    # First task should be high priority
    assert response.data['results'][0]['priority'] == 'high'
