import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fengyun.settings')
django.setup()

from inn_app.models import DutyStaff, Course, Registration

print("開始建立測試資料...")

# 1. 建立值班人員
staff1, _ = DutyStaff.objects.get_or_create(name="阿水伯", defaults={"role": "資深生態嚮導", "is_on_duty": True})
staff2, _ = DutyStaff.objects.get_or_create(name="春嬌姐", defaults={"role": "客棧點心主廚", "is_on_duty": True})
staff3, _ = DutyStaff.objects.get_or_create(name="志明", defaults={"role": "農務體驗達人", "is_on_duty": False})

print(f"-> 已建立值班人員: {staff1.name}, {staff2.name}, {staff3.name}")

# 2. 建立課程
now = timezone.now()

c1, _ = Course.objects.get_or_create(
    title="農村地瓜採收大作戰 (附客棧午餐)",
    defaults={
        "instructor": "志明",
        "description": "跟著志明哥一起來到水井村的有機農地，體驗最接地氣的地瓜採收！適合全家大小一起來挖寶。\n\n活動結束後我們還準備了特製的窯烤地瓜與古早味割稻飯，讓您體驗最真實的三生共好！",
        "capacity": 20,
        "start_time": now + timedelta(days=5, hours=10),
        "end_time": now + timedelta(days=5, hours=14),
        "includes_lunch": True,
        "reg_start_time": now - timedelta(days=1),
        "reg_end_time": now + timedelta(days=3)
    }
)

c2, _ = Course.objects.get_or_create(
    title="極小班！秘境螢火蟲星光夜觀",
    defaults={
        "instructor": "阿水伯",
        "description": "水井村隱藏版的生態秘境！跟著資深的阿水伯深入林間，尋找點點星光的螢火蟲。由於為了維護生態品質，本導覽採取「絕對極小班制」，名額非常稀少！",
        "capacity": 2,
        "start_time": now + timedelta(days=10, hours=19),
        "end_time": now + timedelta(days=10, hours=21),
        "includes_lunch": False
    }
)

c3, _ = Course.objects.get_or_create(
    title="阿嬤的古早味草莓果醬 DIY",
    defaults={
        "instructor": "春嬌姐",
        "description": "採用水井村在地友善農法自種的無毒草莓，春嬌姐將親手教您熬煮出最天然、最甜蜜的草莓果醬！帶一罐甜蜜的記憶回家。",
        "capacity": 15,
        "start_time": now + timedelta(days=7, hours=14),
        "end_time": now + timedelta(days=7, hours=16),
        "includes_lunch": False
    }
)

print(f"-> 已建立課程: {c1.title}, {c2.title}, {c3.title}")

# 3. 建立報名紀錄 (模擬真實狀態)
# 第一堂課：正常報名
Registration.objects.get_or_create(course=c1, phone="0911222333", defaults={"name": "王大明", "email": "ming@test.com", "is_waitlisted": False})
Registration.objects.get_or_create(course=c1, phone="0988777666", defaults={"name": "林小美", "email": "mei@test.com", "is_waitlisted": False})

# 第二堂課：模擬「額滿並觸發候補」
Registration.objects.get_or_create(course=c2, phone="0933444555", defaults={"name": "陳先生", "email": "chen@test.com", "is_waitlisted": False})
Registration.objects.get_or_create(course=c2, phone="0955666777", defaults={"name": "李芳瑜", "email": "lee@test.com", "is_waitlisted": False})
# 這個名單標示為候補
Registration.objects.get_or_create(course=c2, phone="0988111222", defaults={"name": "張同學", "email": "chang@test.com", "is_waitlisted": True})

print(f"-> 已建立報名資料！(包含第二堂課的滿額與候補實驗)")
print("-> 測試資料匯入完成！可以前往前台觀看了。")
