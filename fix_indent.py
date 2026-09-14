import re

with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    c = f.read()

# I did: c.replace("IrrigationAssessment.objects.create(", "update_sustainability_context(request.user)\n            IrrigationAssessment.objects.create(")
# But the original had its own indentation. The exact string replaced didn't account for the leading spaces.
# So "update_sustainability_context" got pasted with whatever leading space the replace had, which might be wrong.
# Let's fix this properly.

# Undo the bad replacements
c = c.replace("update_sustainability_context(request.user)\n            IrrigationAssessment.objects.create(", "IrrigationAssessment.objects.create(")
c = c.replace("update_sustainability_context(request.user)\n            FieldGuardAssessment.objects.create(", "FieldGuardAssessment.objects.create(")
c = c.replace("update_sustainability_context(request.user)\n            CropRecommendation.objects.create(", "CropRecommendation.objects.create(")

# Now redo them with a regex that preserves leading whitespace
c = re.sub(r'([ \t]+)IrrigationAssessment\.objects\.create\(', r'\1update_sustainability_context(request.user)\n\1IrrigationAssessment.objects.create(', c)
c = re.sub(r'([ \t]+)FieldGuardAssessment\.objects\.create\(', r'\1update_sustainability_context(request.user)\n\1FieldGuardAssessment.objects.create(', c)
c = re.sub(r'([ \t]+)CropRecommendation\.objects\.create\(', r'\1update_sustainability_context(request.user)\n\1CropRecommendation.objects.create(', c)

with open('backend/api/views.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Done")
