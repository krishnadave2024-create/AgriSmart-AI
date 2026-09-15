import re

with open('update_crop_backend.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the regex so it only matches up to the closing brace of the dictionary
content = content.replace(
    r"pattern_kb = re.compile(r'CROP_KNOWLEDGE_BASE = \{.*?\}\n', re.DOTALL)",
    r"pattern_kb = re.compile(r'CROP_KNOWLEDGE_BASE = \{.*?^\}', re.DOTALL | re.MULTILINE)"
)

with open('update_crop_backend.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed update_crop_backend.py")
