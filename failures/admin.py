from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SubscriptionPlan, FailureRecord, AIAnalysis, Country, State, City, EcosystemStats, IndustryPerformance

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state__country', 'state')

@admin.register(EcosystemStats)
class EcosystemStatsAdmin(admin.ModelAdmin):
    list_display = ('city', 'total_startups', 'successful_startups', 'success_rate')

@admin.register(IndustryPerformance)
class IndustryPerformanceAdmin(admin.ModelAdmin):
    list_display = ('industry_name', 'city', 'is_successful', 'count')
