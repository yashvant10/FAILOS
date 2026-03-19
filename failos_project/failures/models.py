from django.db import models
from django.contrib.auth.models import AbstractUser

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50) # Basic (Free), Standard, Advanced, Premium
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    features = models.TextField(blank=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)

class FailureRecord(models.Model):
    OUTCOME_CHOICES = [
        ('Failed', 'Failed'),
        ('Passed', 'Passed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='failures')
    title = models.CharField(max_length=200)
    description = models.TextField()
    outcome = models.CharField(max_length=50, choices=OUTCOME_CHOICES, default='Failed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AIAnalysis(models.Model):
    failure_record = models.OneToOneField(FailureRecord, on_delete=models.CASCADE, related_name='analysis')
    possible_reason = models.TextField()
    risk_level = models.CharField(max_length=50)
    suggestion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.failure_record.title}"

class StartupData(models.Model):
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.city}, {self.state} Data"
