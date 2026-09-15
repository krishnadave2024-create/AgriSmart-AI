import re

with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add missing Django DB functions
if 'from django.db.models.functions import TruncDate' not in content:
    content = content.replace('from django.db.models import Count, Avg', 'from django.db.models import Count, Avg\nfrom django.db.models.functions import TruncDate')
    if 'from django.db.models.functions import TruncDate' not in content:
        # Just in case Count, Avg isn't there
        content = 'from django.db.models import Count, Avg\nfrom django.db.models.functions import TruncDate\n' + content


new_dashboard_func = """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    farm = getattr(user, 'farm', None)
    
    # 1. Overview metrics
    disease_scans = DiseaseScan.objects.filter(user=user)
    total_disease_scans = disease_scans.count()
    healthy_scans = disease_scans.filter(predicted_class__icontains='healthy').count()
    diseased_scans = total_disease_scans - healthy_scans
    
    total_crop_recs = CropRecommendationRecord.objects.filter(user=user).count()
    total_irrigations = IrrigationAssessment.objects.filter(user=user).count()
    
    latest_fieldguard = FieldGuardAssessment.objects.filter(user=user).order_by('-created_at').first()
    latest_sustainability = SustainabilityAssessment.objects.filter(user=user).order_by('-created_at').first()
    latest_disease = disease_scans.order_by('-created_at').first()
    latest_crop = CropRecommendationRecord.objects.filter(user=user).order_by('-created_at').first()
    latest_irrigation = IrrigationAssessment.objects.filter(user=user).order_by('-created_at').first()
    
    # 2. Analytics (Time Series)
    # Activity Trend (last 30 days or all time)
    activity_trend = list(ActivityRecord.objects.filter(user=user)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date'))
        
    for item in activity_trend:
        if item['date']:
            item['date'] = item['date'].strftime('%Y-%m-%d')
            
    # FieldGuard Trend
    fg_trend = list(FieldGuardAssessment.objects.filter(user=user).order_by('created_at')[:20].values('created_at', 'score', 'category'))
    for item in fg_trend:
        item['date'] = item['created_at'].strftime('%Y-%m-%d')
        del item['created_at']
        
    # Sustainability Trend
    sus_trend = list(SustainabilityAssessment.objects.filter(user=user).order_by('created_at')[:20].values('created_at', 'score', 'category'))
    for item in sus_trend:
        item['date'] = item['created_at'].strftime('%Y-%m-%d')
        del item['created_at']
        
    # 3. Needs Attention
    needs_attention = []
    
    # Farm Profile checks
    if not farm or not farm.location:
        needs_attention.append({
            'reason': 'Farm city is missing',
            'severity': 'warning',
            'action': 'Update Farm Profile',
            'link': '/farm-profile'
        })
    if not farm or not farm.soil_type:
        needs_attention.append({
            'reason': 'Soil type is not saved',
            'severity': 'info',
            'action': 'Update Farm Profile',
            'link': '/farm-profile'
        })
        
    # Data checks
    if total_disease_scans == 0:
        needs_attention.append({
            'reason': 'No disease scans recorded',
            'severity': 'info',
            'action': 'Run a Disease Scan',
            'link': '/disease'
        })
        
    if latest_fieldguard and latest_fieldguard.score < 40:
        needs_attention.append({
            'reason': f'Latest FieldGuard risk is High ({latest_fieldguard.score}/100)',
            'severity': 'error',
            'action': 'View FieldGuard',
            'link': '/fieldguard'
        })
        
    if not needs_attention and total_disease_scans > 0:
        needs_attention.append({
            'reason': 'No urgent actions detected from your available records.',
            'severity': 'success',
            'action': 'View Analytics',
            'link': '/'
        })

    # 4. Insights
    insights = []
    if latest_disease:
        insights.append(f"Your latest disease scan resulted in '{latest_disease.predicted_class}'.")
    if latest_fieldguard:
        insights.append(f"Your latest FieldGuard assessment is categorized as '{latest_fieldguard.category}'.")
    if latest_crop:
        insights.append(f"Your most recent crop recommendation was '{latest_crop.top_recommendation}'.")
    if latest_sustainability:
        insights.append(f"Your latest sustainability score is {round(latest_sustainability.score)}/100.")
        
    # 5. Recent Activity
    recent_activities = ActivityRecord.objects.filter(user=user).order_by('-created_at')[:6]
    activities_data = [{
        'id': a.id,
        'title': a.title,
        'description': a.description,
        'activity_type': a.activity_type,
        'created_at': a.created_at
    } for a in recent_activities]
    
    return Response({
        'success': True,
        'metrics': {
            'total_disease_scans': total_disease_scans,
            'healthy_scans': healthy_scans,
            'diseased_scans': diseased_scans,
            'total_crop_recommendations': total_crop_recs,
            'total_irrigation_assessments': total_irrigations,
            'latest_disease_date': latest_disease.created_at if latest_disease else None,
            'latest_disease_class': latest_disease.predicted_class if latest_disease else None,
            'latest_crop_rec': latest_crop.top_recommendation if latest_crop else None,
            'latest_irrigation_date': latest_irrigation.created_at if latest_irrigation else None,
            'latest_fieldguard_score': latest_fieldguard.score if latest_fieldguard else None,
            'latest_fieldguard_category': latest_fieldguard.category if latest_fieldguard else None,
            'latest_fieldguard_date': latest_fieldguard.created_at if latest_fieldguard else None,
            'latest_sustainability_score': latest_sustainability.score if latest_sustainability else None,
            'latest_sustainability_category': latest_sustainability.category if latest_sustainability else None,
            'latest_sustainability_date': latest_sustainability.created_at if latest_sustainability else None,
            'missing_profile': not farm or not farm.farm_name or not farm.location
        },
        'analytics': {
            'activity_trend': activity_trend,
            'fieldguard_trend': fg_trend,
            'sustainability_trend': sus_trend,
        },
        'needs_attention': needs_attention,
        'insights': insights,
        'recent_activities': activities_data
    })
"""

# Replace the existing dashboard_summary function
pattern = re.compile(r'@api_view\(\[\'GET\'\]\)\s+@permission_classes\(\[IsAuthenticated\]\)\s+def dashboard_summary\(request\):.*?return Response\(\{.*?\}\)', re.DOTALL)
if pattern.search(content):
    content = pattern.sub(new_dashboard_func.strip(), content)
    with open('backend/api/views.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("dashboard_summary updated successfully.")
else:
    print("Could not find dashboard_summary function to replace.")
