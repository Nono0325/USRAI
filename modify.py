import os
import re

# 1. Modify models.py
models_path = 'inn_app/models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'FileExtensionValidator' not in content:
    content = content.replace('from django.core.validators import MinValueValidator, MaxValueValidator', 'from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator')

def repl(m):
    s = m.group(0).replace('models.ImageField', 'models.FileField')
    if 'validators=' not in s:
        s = s[:-1] + ", validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])]" + s[-1]
    return s

content = re.sub(r'models\.ImageField\([^\)]+\)', repl, content)

if 'map_iframe' not in content:
    content = content.replace("email = models.EmailField('電子郵件', default='service@fengyuninn.com')", "email = models.EmailField('電子郵件', default='service@fengyuninn.com')\n    map_iframe = models.TextField('Google Map 嵌入語法', blank=True, help_text='請貼上 Google Maps 分享的 iframe 語法')")

with open(models_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Create templatetags
os.makedirs('inn_app/templatetags', exist_ok=True)
with open('inn_app/templatetags/__init__.py', 'w', encoding='utf-8') as f:
    f.write('')

filters_content = """from django import template

register = template.Library()

@register.filter(name='is_video')
def is_video(value):
    if not value:
        return False
    ext = str(value).lower().split('.')[-1]
    return ext in ['mp4', 'webm', 'mov']
"""
with open('inn_app/templatetags/custom_filters.py', 'w', encoding='utf-8') as f:
    f.write(filters_content)

print('Models and templatetags updated.')
