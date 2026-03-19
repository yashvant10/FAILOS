from django.db import models
from django.contrib.auth.models import AbstractUser

class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('BASIC', 'Basic (Free)'),
        ('STANDARD', 'Standard'),
        ('ADVANCED', 'Advanced'),
        ('PREMIUM', 'Premium'),
    ]
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    features = models.TextField(help_text="Comma-separated list of features", blank=True)

    def __str__(self):
        return self.get_name_display()

class User(AbstractUser):
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    
    # Profile fields
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    
    # Settings & Privacy
    two_factor_enabled = models.BooleanField(default=False)
    email_alerts_enabled = models.BooleanField(default=True)
    ai_notifications_enabled = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=False)
    share_ideas_publicly = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

class FailureRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='failures')
    title = models.CharField(max_length=255)
    description = models.TextField()
    city = models.CharField(max_length=100, default='Unknown')
    city_model = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, related_name='failures_logged')
    state = models.CharField(max_length=100, default='Unknown')
    state_model = models.ForeignKey('State', on_delete=models.SET_NULL, null=True, blank=True, related_name='failures_logged')
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    date_submitted = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

class AIAnalysis(models.Model):
    failure_record = models.OneToOneField(FailureRecord, on_delete=models.CASCADE, related_name='analysis')
    possible_reason = models.TextField()
    risk_level = models.CharField(max_length=50, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')])
    suggestion = models.TextField()
    prediction = models.CharField(max_length=50, choices=[('HIGH_SUCCESS', 'High Success Probability'), ('LOW_SUCCESS', 'Low Success Probability')])
    
    # Interpreted Data from messy input
    interpreted_title = models.CharField(max_length=255, blank=True)
    interpreted_description = models.TextField(blank=True)
    interpreted_business_type = models.CharField(max_length=100, blank=True)
    
    # Feature 1 & 3: Suggestions & Success Score
    success_score = models.IntegerField(default=0)
    improvement_suggestions_list = models.TextField(blank=True, help_text="JSON list of suggestions")
    
    # Feature 1: AI Market Demand Analyzer
    market_demand_score = models.IntegerField(default=0)
    market_demand_level = models.CharField(max_length=50, default='Unknown')
    market_demand_reason = models.TextField(blank=True)
    market_demand_suggestion = models.TextField(blank=True)
    
    # Feature 2: AI Cost Estimator
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    budget_status = models.CharField(max_length=50, default='Unknown')
    budget_suggestion = models.TextField(blank=True)
    
    # Feature 3: AI Competitor Analyzer
    competition_level = models.CharField(max_length=50, default='Unknown')
    competition_reason = models.TextField(blank=True)
    competition_suggestion = models.TextField(blank=True)
    
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for: {self.failure_record.title}"

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True)
    def __str__(self): return self.name

class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    def __str__(self): return f"{self.name}, {self.country.name}"

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    def __str__(self): return f"{self.name}, {self.state.name}"

class EcosystemStats(models.Model):
    city = models.OneToOneField(City, on_delete=models.CASCADE, related_name='stats')
    total_startups = models.IntegerField(default=0)
    successful_startups = models.IntegerField(default=0)
    failed_startups = models.IntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    growth_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Annual growth percentage")
    last_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.total_startups > 0:
            self.success_rate = (self.successful_startups / self.total_startups) * 100
        super().save(*args, **kwargs)

    def __str__(self): return f"Stats for {self.city.name}"

class IndustryPerformance(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='industries')
    industry_name = models.CharField(max_length=100)
    is_successful = models.BooleanField(default=True, help_text="True for successful, False for failed")
    count = models.IntegerField(default=0)

    def __str__(self):
        status = "Successful" if self.is_successful else "Failed"
        return f"{self.industry_name} ({status}) in {self.city.name}"
