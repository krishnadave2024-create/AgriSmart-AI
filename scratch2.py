import re

with open('backend/api/tests.py', 'r', encoding='utf-8') as f:
    c = f.read()

c = re.sub(r"('temperature': 30, 'rainfall': 10)", r"'crop': 'Wheat', \1", c)
c = re.sub(r"('temperature': 36, 'rainfall': 0)", r"'crop': 'Wheat', \1", c)

with open('backend/api/tests.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done')
