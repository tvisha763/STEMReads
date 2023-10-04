from django.db import models
from django.forms import CharField
from django.utils import timezone
# Create your models here.


class User(models.Model):
    STATUS = [
        (1, 'User'),
        (2, 'Admin'),
    ]
    username = models.CharField(max_length=30, unique=True)
    email = models.CharField(max_length=30)
    phone = models.CharField(max_length=10, default='')
    password = models.CharField(max_length=1000)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    salt = models.CharField(max_length=1023)
    status = models.IntegerField(default=1, choices=STATUS)
    def __str__(self):
        return '%s - %s' % (self.username, self.status)

    
class Post(models.Model):
    title = models.CharField(max_length=30, unique=True)
    author = models.CharField(max_length=30)
    video_embed = models.CharField(max_length=1000, default=None)
    text = models.TextField(unique=True)
    image = models.ImageField(upload_to='media')
    def __str__(self):
        return '%s - %s' % (self.title, self.author)
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.IntegerField(default=None)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s' % (self.user.username, self.post_id)
    

class Staff(models.Model):
    name = models.CharField(max_length=90, unique=True)
    image = models.ImageField(upload_to='media')
    description = models.TextField(unique=True)

    def __str__(self):
        return self.name
    
class Request(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=90, unique=True)
    request = models.TextField(unique=True)
    taken_by = models.CharField(max_length=90, default = '')
    
    def __str__(self):
        return '%s - %s' % (self.title, self.taken_by)