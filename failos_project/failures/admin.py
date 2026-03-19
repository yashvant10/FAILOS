from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SubscriptionPlan, FailureRecord, AIAnalysis, StartupData

admin.site.register(User, UserAdmin)
admin.site.register(SubscriptionPlan)
admin.site.register(FailureRecord)
admin.site.register(AIAnalysis)
admin.site.register(StartupData)
