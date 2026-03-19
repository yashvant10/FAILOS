from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home_page, name='home'),
    path('demo/', views.demo_dashboard, name='demo_dashboard'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),

    # Dashboard & Failures
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-failure/', views.add_failure, name='add_failure'),
    path('failure/<int:pk>/', views.failure_details, name='failure_details'),
    path('failure/<int:pk>/edit/', views.edit_failure, name='edit_failure'),
    path('failure/<int:pk>/download/', views.download_report, name='download_report'),
    path('history/', views.history_page, name='history'),
    path('profile/', views.profile_page, name='profile'),

    # Analysis & AI
    path('analytics/', views.analytics_page, name='analytics'),
    path('search/', views.search_page, name='search'),
    path('filter/', views.filter_page, name='filter'),
    path('idea-outcomes/', views.idea_outcomes, name='idea_outcomes'),
    path('startup-insights/', views.startup_insights, name='startup_insights'),

    # Admin / Management
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-failures/', views.manage_failures, name='manage_failures'),
    path('manage-users/toggle-premium/<int:user_id>/', views.toggle_user_premium, name='toggle_user_premium'),
    path('manage-users/toggle-staff/<int:user_id>/', views.toggle_user_staff, name='toggle_user_staff'),

    # Premium Settings
    path('pricing/', views.pricing_page, name='pricing'),
    path('payment/', views.payment_page, name='payment'),
    path('payment/paytm/', views.paytm_payment, name='paytm_payment'),
    path('payment/paytm-success/', views.paytm_success, name='paytm_success'),
    
    # Settings
    path('settings/', views.settings_page, name='settings'),
    path('notifications/', views.notifications_page, name='notifications'),
    # Startup Insights
    path('insights/', views.startup_insights_page, name='startup_insights'),
    path('api/states/<int:country_id>/', views.get_states, name='api_states'),
    path('api/cities/<int:state_id>/', views.get_cities, name='api_cities'),
    path('api/city-stats/<int:city_id>/', views.get_city_stats_api, name='api_city_stats'),
    path('api/predict-success/', views.predict_startup_success_api, name='api_predict_success'),
]
