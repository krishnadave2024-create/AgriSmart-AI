with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    
    # After DiseaseScan.objects.create
    if "scan = DiseaseScan.objects.create(" in line:
        indent = line.split("scan = ")[0]
        new_lines.append(indent + "Notification.objects.create(user=user, title='New Disease Scan', message=f'Scan completed: {predicted_class}', notification_type='disease_scan', related_route='/disease')\n")

    # After CropRecommendationRecord.objects.create
    if "CropRecommendationRecord.objects.create(" in line and 'user=user' in line and 'top_recommendation=top_recommendation' in line:
        indent = line.split("CropRecommendationRecord")[0]
        new_lines.append(indent + "Notification.objects.create(user=user, title='Crop Recommendation', message=f'Recommended: {top_recommendation}', notification_type='crop_recommendation', related_route='/crops')\n")
        
    # After IrrigationAssessment.objects.create
    if "irr_obj = IrrigationAssessment.objects.create(" in line:
        indent = line.split("irr_obj = ")[0]
        new_lines.append(indent + "Notification.objects.create(user=user, title='Irrigation Assessment', message=f'Priority: {priority}', notification_type='irrigation_assessment', related_route='/irrigation')\n")

    # After FieldGuardAssessment.objects.create
    if "fg_obj = FieldGuardAssessment.objects.create(" in line:
        indent = line.split("fg_obj = ")[0]
        new_lines.append(indent + "Notification.objects.create(user=user, title='FieldGuard Assessment', message=f'Risk Category: {category}', notification_type='fieldguard_assessment', related_route='/fieldguard')\n")

with open('backend/api/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Added triggers")
