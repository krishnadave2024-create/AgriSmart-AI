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

# Inject update_sustainability_context call into recommend_irrigation
c = re.sub(
    r'(?m)^(\s+)(return Response\(\{[\'"]success[\'"]:\s*True,\s*[\'"]irrigation_priority[\'"])',
    r'\1update_sustainability_context(request.user)\n\1\2',
    c
)

# Inject update_sustainability_context call into fieldguard_assess
c = re.sub(
    r'(?m)^(\s+)(return Response\(\{[\'"]success[\'"]:\s*True,\s*[\'"]score[\'"])',
    r'\1update_sustainability_context(request.user)\n\1\2',
    c
)

# Inject update_sustainability_context call into recommend_crop
c = re.sub(
    r'(?m)^(\s+)(return Response\(\{[\'"]success[\'"]:\s*True,\s*[\'"]recommendations[\'"])',
    r'\1update_sustainability_context(request.user)\n\1\2',
    c
)

with open('backend/api/views.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done')
