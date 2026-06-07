from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

class EmailAccountPasswordVerification(models.Model):
    TOKEN_TYPE_CHOICES = [
        ('EMAIL_VERIFICATION', 'Email Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.token_type}"