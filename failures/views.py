from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import json
from django.db.models import Count
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import User, FailureRecord, AIAnalysis, Country, State, City, EcosystemStats, IndustryPerformance, SubscriptionPlan
from .ai_agent import analyze_failure

# Public Pages
def landing_page(request):
    return render(request, 'landing.html')

def demo_dashboard(request):
    return render(request, 'demo_dashboard.html')

def home_page(request):
    return render(request, 'home.html')

def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
    return render(request, 'contact.html')

# Authentication
def login_view(request):
    if request.method == 'POST':
        try:
            u = request.POST.get('username')
            p = request.POST.get('password')
            user = authenticate(request, username=u, password=p)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        except Exception as e:
            import traceback
            print(f"LOGIN ERROR: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"Login Error: {str(e)}")
            return render(request, 'login.html')
    return render(request, 'login.html')

def signup_view(request):
    if request.method == 'POST':
        try:
            u = request.POST.get('username')
            e = request.POST.get('email')
            p = request.POST.get('password')
            fn = request.POST.get('first_name', '')
            ln = request.POST.get('last_name', '')
            if User.objects.filter(username=u).exists():
                messages.error(request, "Username already taken.")
            else:
                user = User.objects.create_user(username=u, email=e, password=p, first_name=fn, last_name=ln)
                login(request, user)
                messages.success(request, "Account created successfully!")
                return redirect('dashboard')
        except Exception as e:
            import traceback
            print(f"SIGNUP ERROR: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"Signup Error: {str(e)}")
            return render(request, 'signup.html')
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

def forgot_password(request):
    return render(request, 'forgot_password.html')

# Dashboard & Failures
@login_required
def dashboard(request):
    failures = FailureRecord.objects.filter(user=request.user).select_related('analysis').order_by('-date_submitted')[:5]
    ai_analysis_count = AIAnalysis.objects.filter(failure_record__user=request.user).count()
    return render(request, 'dashboard.html', {
        'recent_failures': failures,
        'ai_analysis_count': ai_analysis_count
    })

@login_required
def add_failure(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        # Get location data
        city_id = request.POST.get('city_id')
        state_id = request.POST.get('state_id')
        
        city_obj = None
        state_obj = None
        city_name = 'Unknown'
        state_name = 'Unknown'
        
        if city_id:
            city_obj = City.objects.filter(id=city_id).select_related('state').first()
            if city_obj:
                city_name = city_obj.name
                state_obj = city_obj.state
                state_name = state_obj.name
        elif state_id:
            state_obj = State.objects.filter(id=state_id).first()
            if state_obj:
                state_name = state_obj.name
        
        # Get budget and handle empty strings
        budget_raw = request.POST.get('budget', '0.00').strip()
        budget = budget_raw if budget_raw else '0.00'
        is_public = request.POST.get('is_public') == 'on'
        
        # Save record
        record = FailureRecord.objects.create(
            user=request.user,
            title=title,
            description=description,
            state=state_name,
            state_model=state_obj,
            city=city_name,
            city_model=city_obj,
            budget=budget,
            is_public=is_public
        )
        
        # Trigger AI Analysis
        analysis_data = analyze_failure(title, description, state_name, city_name, budget)
        AIAnalysis.objects.create(
            failure_record=record,
            interpreted_title=analysis_data['interpreted_idea']['title'],
            interpreted_description=analysis_data['interpreted_idea']['description'],
            interpreted_business_type=analysis_data['interpreted_idea']['business_type'],
            possible_reason=analysis_data['possible_reason'],
            risk_level=analysis_data['risk_level'],
            prediction=analysis_data['prediction'],
            suggestion=analysis_data['suggestion'],
            market_demand_score=analysis_data['market_demand_score'],
            market_demand_level=analysis_data['market_demand_level'],
            market_demand_reason=analysis_data['market_demand_reason'],
            market_demand_suggestion=analysis_data['market_demand_suggestion'],
            estimated_cost=analysis_data['estimated_cost'],
            budget_status=analysis_data['budget_status'],
            budget_suggestion=analysis_data['budget_suggestion'],
            competition_level=analysis_data['competition_level'],
            competition_reason=analysis_data['competition_reason'],
            competition_suggestion=analysis_data['competition_suggestion'],
            success_score=analysis_data['success_score'],
            improvement_suggestions_list=analysis_data['improvement_suggestions_list']
        )
        
        messages.success(request, "Failure recorded and analyzed successfully!")
        return redirect('failure_details', pk=record.id)

    countries = Country.objects.all()
    return render(request, 'add_failure.html', {'countries': countries})

@login_required
def failure_details(request, pk):
    failure = get_object_or_404(FailureRecord, pk=pk)
    # If not the owner and not public, block access unless staff
    if failure.user != request.user and not failure.is_public and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this.")
        return redirect('dashboard')
        
    # Feature 4: Similar Idea Detection
    # Basic keyword matching against words > 4 chars in the title
    title_words = [word.lower() for word in failure.title.split() if len(word) > 4]
    similar_ideas = []
    
    if title_words:
        all_other_failures = FailureRecord.objects.exclude(id=failure.id)
        for other in all_other_failures:
            if any(word in other.title.lower() or word in other.description.lower() for word in title_words):
                if other not in similar_ideas:
                    similar_ideas.append(other)
                    if len(similar_ideas) >= 3: # Limit to 3 similar ideas
                        break
                        
    # Parse the suggestions list
    try:
        suggestions_list = json.loads(failure.analysis.improvement_suggestions_list)
    except:
        suggestions_list = []
        
    context = {
        'failure': failure,
        'similar_ideas': similar_ideas,
        'suggestions_list': suggestions_list
    }
    return render(request, 'failure_details.html', context)

@login_required
def edit_failure(request, pk):
    failure = get_object_or_404(FailureRecord, pk=pk)
    # Check permission: owner or staff
    if failure.user != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to edit this record.")
        return redirect('dashboard')
    if request.method == 'POST':
        if 'delete' in request.POST:
            failure.delete()
            messages.success(request, "Record deleted.")
            return redirect('dashboard')
            
        # Get location data
        city_id = request.POST.get('city_id')
        state_id = request.POST.get('state_id')
        
        city_obj = None
        state_obj = None
        city_name = failure.city
        state_name = failure.state
        
        if city_id:
            city_obj = City.objects.filter(id=city_id).select_related('state').first()
            if city_obj:
                city_name = city_obj.name
                state_obj = city_obj.state
                state_name = state_obj.name
        elif state_id:
            state_obj = State.objects.filter(id=state_id).first()
            if state_obj:
                state_name = state_obj.name

        failure.title = request.POST.get('title')
        failure.description = request.POST.get('description')
        failure.city = city_name
        failure.city_model = city_obj
        failure.state = state_name
        failure.state_model = state_obj
        # Get budget and handle empty strings
        budget_raw = request.POST.get('budget', '').strip()
        failure.budget = budget_raw if budget_raw else failure.budget
        failure.is_public = request.POST.get('is_public') == 'on'
        failure.save()
        
        # Re-analyze
        analysis_data = analyze_failure(failure.title, failure.description, failure.state, failure.city, failure.budget)
        # Update or create AI analysis
        AIAnalysis.objects.update_or_create(
            failure_record=failure,
            defaults={
                'possible_reason': analysis_data['possible_reason'],
                'risk_level': analysis_data['risk_level'],
                'prediction': analysis_data['prediction'],
                'suggestion': analysis_data['suggestion'],
                'market_demand_score': analysis_data['market_demand_score'],
                'market_demand_level': analysis_data['market_demand_level'],
                'market_demand_reason': analysis_data['market_demand_reason'],
                'market_demand_suggestion': analysis_data['market_demand_suggestion'],
                'estimated_cost': analysis_data['estimated_cost'],
                'budget_status': analysis_data['budget_status'],
                'budget_suggestion': analysis_data['budget_suggestion'],
                'competition_level': analysis_data['competition_level'],
                'competition_reason': analysis_data['competition_reason'],
                'competition_suggestion': analysis_data['competition_suggestion'],
                'success_score': analysis_data['success_score'],
                'improvement_suggestions_list': analysis_data['improvement_suggestions_list']
            }
        )
        
        messages.success(request, "Record updated.")
        return redirect('failure_details', pk=failure.id)
        
    countries = Country.objects.all()
    return render(request, 'edit_failure.html', {'failure': failure, 'countries': countries})

@login_required
def history_page(request):
    failures = FailureRecord.objects.filter(user=request.user).order_by('-date_submitted')
    return render(request, 'history.html', {'failures': failures})

@login_required
def profile_page(request):
    user = request.user
    failures = FailureRecord.objects.filter(user=user)
    total_ideas = failures.count()
    analyses = AIAnalysis.objects.filter(failure_record__user=user)
    total_analyses = analyses.count()
    success_predictions = analyses.filter(prediction='HIGH_SUCCESS').count()
    failure_predictions = analyses.filter(prediction='LOW_SUCCESS').count()
    
    recent_activity = failures.select_related('analysis').order_by('-date_submitted')[:5]
    
    context = {
        'total_ideas': total_ideas,
        'total_analyses': total_analyses,
        'success_predictions': success_predictions,
        'failure_predictions': failure_predictions,
        'recent_activity': recent_activity
    }
    return render(request, 'profile.html', context)

# Analysis & AI
@login_required
def analytics_page(request):
    # Feature 2: Failure Pattern Detection
    all_analyses = AIAnalysis.objects.all()
    total_analyses = all_analyses.count()
    
    # Calculate top failure reasons by matching keywords in possible_reason
    reason_patterns = {
        'Low Budget / Funding': ['money', 'funding', 'capital', 'runway', 'expensive', 'cost', 'under-capitalized'],
        'High Competition': ['competition', 'rival', 'google', 'facebook', 'monopoly'],
        'Poor Market Demand': ['market', 'users', 'customers', 'sales', 'demand', 'nobody'],
        'Team / Execution Issues': ['team', 'founder', 'fight', 'talent', 'hire', 'developer'],
        'Unvalidated Assumptions': ['unvalidated']
    }
    
    top_reasons = {}
    if total_analyses > 0:
        for analysis in all_analyses:
            if hasattr(analysis, 'possible_reason') and analysis.possible_reason:
                reason = analysis.possible_reason.lower()
                for key, words in reason_patterns.items():
                    if any(word in reason for word in words):
                        top_reasons[key] = top_reasons.get(key, 0) + 1
                    
        # Calculate percentages
        top_reasons = {k: int((v / total_analyses) * 100) for k, v in top_reasons.items()}
        # Sort descending
        top_reasons = dict(sorted(top_reasons.items(), key=lambda item: item[1], reverse=True))

    return render(request, 'analytics.html', {
        'top_reasons': top_reasons,
        'total_analyses': total_analyses
    })

@login_required
def search_page(request):
    return render(request, 'search.html')

@login_required
def filter_page(request):
    return render(request, 'filter.html')
    
@login_required
def download_report(request, pk):
    # Feature 5: AI Startup Report Download
    failure = get_object_or_404(FailureRecord, pk=pk)
    
    # Ensure they have permission to download
    if failure.user != request.user and not failure.is_public and not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)
        
    if not hasattr(failure, 'analysis') or not failure.analysis:
        return HttpResponse("Report not available yet. Please wait for AI analysis to complete.", status=404)
        
    analysis = failure.analysis
    
    # Build text report content
    report_content = f"Startup Analysis Report\n\n"
    report_content += f"Idea: {failure.title}\n"
    report_content += f"Budget: ₹{failure.budget}\n"
    report_content += f"Location: {failure.city}, {failure.state}\n\n"
    
    report_content += f"Risk Level: {analysis.get_risk_level_display()}\n"
    report_content += f"Demand Score: {analysis.market_demand_score}%\n"
    report_content += f"Success Probability: {analysis.success_score}%\n\n"
    
    report_content += f"Recommendation:\n"
    report_content += f"{analysis.suggestion}\n"
    
    # Create the HTTP response
    response = HttpResponse(report_content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="analysis_{failure.id}.txt"'
    
    return response

def idea_outcomes(request):
    return render(request, 'idea_outcomes.html')

def startup_insights(request):
    return render(request, 'startup_insights.html')

# Admin / Management
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    user_count = User.objects.count()
    failure_count = FailureRecord.objects.count()
    premium_users = User.objects.filter(is_premium=True).count()
    total_analyses = AIAnalysis.objects.count()
    recent_failures = FailureRecord.objects.select_related('user', 'analysis').order_by('-date_submitted')[:10]
    
    context = {
        'user_count': user_count,
        'failure_count': failure_count,
        'premium_users': premium_users,
        'total_analyses': total_analyses,
        'recent_failures': recent_failures
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_users(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_failures(request):
    failures = FailureRecord.objects.select_related('user').all().order_by('-date_submitted')
    return render(request, 'manage_failures.html', {'failures': failures})

@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_user_premium(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    target_user.is_premium = not target_user.is_premium
    target_user.save()
    messages.success(request, f"Premium status for {target_user.username} updated.")
    return redirect('manage_users')

@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_user_staff(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    # Prevent self-demotion to avoid locking out the last admin
    if target_user == request.user:
        messages.error(request, "You cannot change your own staff status.")
    else:
        target_user.is_staff = not target_user.is_staff
        target_user.save()
        messages.success(request, f"Staff status for {target_user.username} updated.")
    return redirect('manage_users')

# Premium Settings
def pricing_page(request):
    return render(request, 'pricing.html')

@login_required
def payment_page(request):
    return render(request, 'payment.html')

@login_required
def paytm_payment(request):
    return render(request, 'paytm_payment.html')

@login_required
def paytm_success(request):
    request.user.is_premium = True
    request.user.save()
    messages.success(request, "Account upgraded to Premium!")
    return render(request, 'paytm_success.html')

# Settings
@login_required
def settings_page(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_account':
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.city = request.POST.get('city', '')
            request.user.state = request.POST.get('state', '')
            request.user.save()
            messages.success(request, "Account information updated.")
            
        elif action == 'update_security':
            # Simplified security update
            password = request.POST.get('new_password')
            if password:
                request.user.set_password(password)
                request.user.save()
                messages.success(request, "Password updated successfully. Please login again.")
                return redirect('login')
                
        elif action == 'update_notifications':
            request.user.email_alerts_enabled = request.POST.get('email_alerts') == 'on'
            request.user.ai_notifications_enabled = request.POST.get('ai_notifications') == 'on'
            request.user.save()
            messages.success(request, "Notification preferences updated.")
            
        elif action == 'delete_account':
            user = request.user
            logout(request)
            user.delete()
            messages.warning(request, "Your account has been permanently deleted.")
            return redirect('login')
            
        return redirect('settings')
        
    return render(request, 'settings.html')

@login_required
def notifications_page(request):
    return render(request, 'notifications.html')
# Startup Insights API
@login_required
def get_states(request, country_id):
    states = State.objects.filter(country_id=country_id).values('id', 'name')
    return JsonResponse(list(states), safe=False)

@login_required
def get_cities(request, state_id):
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)

@login_required
def get_city_stats_api(request, city_id):
    city = get_object_or_404(City, id=city_id)
    stats = getattr(city, 'stats', None)
    
    if not stats:
        return JsonResponse({'error': 'No data for this city'}, status=404)
        
    industries = city.industries.all()
    success_industries = [i.industry_name for i in industries if i.is_successful]
    failed_industries = [i.industry_name for i in industries if not i.is_successful]
    
    # Fetch real failure records for this city and their risk levels
    raw_failures = FailureRecord.objects.filter(city__iexact=city.name).select_related('analysis')[:5]
    city_failures = []
    for f in raw_failures:
        city_failures.append({
            'id': f.id,
            'title': f.title,
            'description': f.description,
            'risk_level': getattr(f.analysis, 'risk_level', 'MEDIUM') if hasattr(f, 'analysis') else 'MEDIUM'
        })
    
    data = {
        'location': f"{city.name}, {city.state.name}, {city.state.country.name}",
        'total': stats.total_startups,
        'success': stats.successful_startups,
        'failed': stats.failed_startups,
        'rate': float(stats.success_rate),
        'growth': float(stats.growth_rate),
        'success_industries': success_industries,
        'failed_industries': failed_industries,
        'city_failures': city_failures,
    }
    return JsonResponse(data)

@login_required
def startup_insights_page(request):
    countries = Country.objects.all()
    return render(request, 'startup_insights.html', {'countries': countries})

@login_required
def predict_startup_success_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            idea = data.get('idea')
            location = data.get('location')
            
            # Use the common analysis agent logic for consistency
            analysis_data = analyze_failure(idea, "Success prediction request", "Unknown", location, 0)
            return JsonResponse({
                'success_probability': analysis_data['success_score'],
                'risk_level': analysis_data['risk_level'],
                'reasons': analysis_data['improvement_suggestions_list'], # suggestions as reasons
                'insight': analysis_data['suggestion']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
