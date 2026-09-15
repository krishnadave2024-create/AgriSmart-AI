with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    backend = f.readlines()

new_backend = []
for line in backend:
    new_backend.append(line)
    if 'from rest_framework.decorators import permission_classes' in line:
        new_backend.append('from .serializers import NotificationSerializer\n')
        new_backend.append('from .models import Notification\n')

with open('backend/api/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_backend)

print("Import added.")
