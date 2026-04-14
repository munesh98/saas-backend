from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta
# Create your models here.

User = get_user_model()

class Plan(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    auto_renew = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.plan} - {self.status}"


    