with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Add imports if missing
if 'Notification' not in c:
    c = c.replace('from .models import UserProfile, FarmProfile, DiseaseScan, CropRecommendationRecord, IrrigationAssessment, FieldGuardAssessment, SustainabilityAssessment', 
                  'from .models import UserProfile, FarmProfile, DiseaseScan, CropRecommendationRecord, IrrigationAssessment, FieldGuardAssessment, SustainabilityAssessment, Notification')

if 'NotificationSerializer' not in c:
    c = c.replace('from .serializers import RegisterSerializer, UserProfileSerializer, FarmProfileSerializer',
                  'from .serializers import RegisterSerializer, UserProfileSerializer, FarmProfileSerializer, NotificationSerializer')

new_views = """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    try:
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        unread_count = notifications.filter(is_read=False).count()
        return Response({
            'success': True,
            'notifications': serializer.data,
            'unread_count': unread_count
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'success': False, 'error': 'Notification not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    try:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'success': True})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def navbar_weather(request):
    try:
        farm = FarmProfile.objects.filter(user=request.user).first()
        if not farm or not farm.location:
            return Response({'success': False, 'error': 'Farm city not set.'}, status=400)
            
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        if not api_key or api_key == 'your_openweather_api_key_here':
            return Response({'success': False, 'error': 'Weather service not configured.'}, status=503)
            
        url = f"http://api.openweathermap.org/data/2.5/weather?q={farm.location}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            return Response({
                'success': True,
                'temp': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'location': farm.location
            })
        else:
            return Response({'success': False, 'error': 'Failed to fetch weather data.'}, status=503)
            
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
"""

if 'def get_notifications' not in c:
    c += new_views
    with open('backend/api/views.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Views added")
else:
    print("Views already exist")
