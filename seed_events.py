import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fengyun.settings')
django.setup()

from inn_app.models import Event

events = [
    {
        'title': '春季賞花攝影比賽',
        'description': '水井村最美的春天就在這裡！歡迎攝影愛好者捕捉花海美景，豐富獎品等你拿。',
        'date': datetime.date(2026, 4, 15)
    },
    {
        'title': '在地農夫市集',
        'description': '產地直送，支持在地小農。這裡有最新鮮的在地蔬菜與手作特色產品。',
        'date': datetime.date(2026, 4, 20)
    },
    {
        'title': '星空下的露天音樂會',
        'description': '在微風徐徐的夜晚，享受當地的民謠歌聲，度過一個難忘的夜晚。',
        'date': datetime.date(2026, 5, 2)
    },
    {
        'title': '傳統工藝編織坊',
        'description': '跟著客棧的資深達人一起學習傳統的竹編工藝，親手製作屬於自己的生活藝術。',
        'date': datetime.date(2026, 5, 10)
    },
    {
        'title': '水井村歷史古道導覽',
        'description': '由在地文史工作者帶領，探尋水井村不為人知的故事與百年古道的幽靜。',
        'date': datetime.date(2026, 5, 15)
    }
]

for e in events:
    Event.objects.get_or_create(
        title=e['title'],
        description=e['description'],
        date=e['date']
    )

print("Sample events created successfully!")
