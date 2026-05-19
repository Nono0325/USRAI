from django import template

register = template.Library()

@register.filter(name='is_video')
def is_video(value):
    if not value:
        return False
    ext = str(value).lower().split('.')[-1]
    return ext in ['mp4', 'webm', 'mov']
