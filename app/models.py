from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='images/prof_pic/')

class Base(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_created")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="%(class)s_updated")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True  

    def __str__(self):
        return f"Created by {self.created_by.username}"
   
class Status(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class AndroidApp(Base):
    app_name = models.CharField(max_length=255, unique=True)
    package_name = models.CharField(max_length=255, unique=True)
    app_logo = models.ImageField(upload_to='images/app_logo/', null=True, blank=True)
    app_version = models.CharField(max_length=50)
    category = models.CharField(max_length=100)
    contact_email = models.EmailField()

    def __str__(self):
        return self.app_name
    
class TaskManager(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_created')
    android_app = models.ForeignKey(AndroidApp, on_delete=models.CASCADE, related_name='app_tasks')
    points = models.IntegerField(default=0)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    screenshot = models.ImageField(upload_to='images/task_screenshots/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.android_app.app_name}"
    


