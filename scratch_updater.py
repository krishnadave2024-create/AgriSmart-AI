import re

with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace sustainability_score block completely
start_marker = "@api_view(['POST'])\ndef sustainability_score(request):"
end_marker = "@api_view(['POST'])\ndef farmer_assistant(request):"
if start_marker in c and end_marker in c:
    s_idx = c.find(start_marker)
    e_idx = c.find(end_marker)
    
    with open('backend/api/temp_sust.py', 'r', encoding='utf-8') as f2:
        new_sust = f2.read()
        
    c = c[:s_idx] + new_sust + "\n\n" + c[e_idx:]

# Inject update_sustainability_context calls
def inject_call(func_name, code):
    # Find return Response({'success': True... in the function and prepend the update call
    # This is a bit tricky, let's just do a string replace on the return Response inside the success block
    pass

# Quick and dirty:
c = c.replace(
    "IrrigationAssessment.objects.create(",
    "update_sustainability_context(request.user)\n            IrrigationAssessment.objects.create("
)
c = c.replace(
    "FieldGuardAssessment.objects.create(",
    "update_sustainability_context(request.user)\n            FieldGuardAssessment.objects.create("
)
c = c.replace(
    "CropRecommendation.objects.create(",
    "update_sustainability_context(request.user)\n            CropRecommendation.objects.create("
)

# implement the actual update_sustainability_context
update_func = """def update_sustainability_context(user):
    class DummyRequest:
        def __init__(self, u):
            self.user = u
            self.data = {}
    try:
        sustainability_score(DummyRequest(user))
    except Exception:
        pass
"""
c = c.replace("def update_sustainability_context(user):\n    # Used for automatic updates after other modules run\n    try:\n        # A simple internal hook: create a dummy request object and pass it to sustainability_score?\n        # Better: just factor out the logic, but to save time, we'll just let the frontend trigger it or do it inline.\n        pass\n    except Exception:\n        pass", update_func)

with open('backend/api/views.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done')
