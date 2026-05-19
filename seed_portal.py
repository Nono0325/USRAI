import os
import django
import datetime
from django.core.files import File
import requests
from io import BytesIO

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fengyun.settings')
django.setup()

from inn_app.models import Story, USRAchievement, TechProject, ExperienceCourse, Service, TechSection

def download_image(url, folder, filename):
    """Utility to download image and return a Django-ready File object."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return File(BytesIO(response.content), name=filename)
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return None

# Ensure folders exist
media_folders = ['services', 'tech', 'tech_sections', 'stories', 'achievements', 'workshops']
for folder in media_folders:
    os.makedirs(os.path.join('media', folder), exist_ok=True)

print("--- Seeding Triple Harmony Services ---")
services_data = [
    {
        'title': '在地生產：智慧漁業與農創',
        'description': '導入 AIoT 監控系統，實現傳統漁塭轉型，提升產能並確保品質穩定，從土地到餐桌的真實美味。',
        'img_url': 'https://images.unsplash.com/photo-1542314831-c6a4d14effb0?q=80&w=800&auto=format&fit=crop'
    },
    {
        'title': '生態生活：永續聚落體驗',
        'description': '在風雲客棧，我們與大自然共生。透過節水技術與減碳計畫，打造宜居的綠色生活圈。',
        'img_url': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=800&auto=format&fit=crop'
    },
    {
        'title': '生命共好：青銀共創共享',
        'description': '結合大學生的創意與在地長輩的智慧，推動藝術工作坊與在地導覽，延續村落生命力。',
        'img_url': 'https://images.unsplash.com/photo-1490730141103-6cac27aaab94?q=80&w=800&auto=format&fit=crop'
    }
]

for s in services_data:
    obj, created = Service.objects.get_or_create(
        title=s['title'], 
        defaults={'description': s['description']}
    )
    if not created:
        obj.description = s['description']
    
    if not obj.image:
        img_file = download_image(s['img_url'], 'services', f"{s['title']}.jpg")
        if img_file:
            obj.image.save(f"{s['title']}.jpg", img_file, save=False)
    obj.is_active = True
    obj.save()

print("--- Seeding Tech Sections & Projects ---")
tech_sections_data = [
    {
        'title': 'AIoT 智慧應用',
        'intro_text': '我們在魚塭部署了多種感測器，透過雲端系統即時監控水質與設備狀態，並自動化調整環境參數。',
        'layout_type': 'side_image',
        'img_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop',
        'projects': [
            {
                'name': '水質監控大數據平台',
                'description': '24小時不間斷監測溶氧(DO)、pH值及水溫，異常時手機自動推播警報，確保魚蝦健康。',
                'img_url': 'https://images.unsplash.com/photo-1558485940-84fe9573656b?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': '智慧減碳節水系統',
                'description': '利用自動化閥門與循環水技術，大幅降低養殖用水量，並優化能源效率以達成節能目標。',
                'img_url': 'https://images.unsplash.com/photo-1466692476868-aef1dfb1e835?q=80&w=600&auto=format&fit=crop'
            }
        ]
    },
    {
        'title': 'AR 互動與漫遊導覽',
        'intro_text': '透過擴增實境 (AR) 技術，遊客只需掃描指定 QR Code，便能與水井村 Q 版代言人互動，聽取地方故事。',
        'layout_type': 'side_text',
        'img_url': 'https://images.unsplash.com/photo-1592478411213-6153e4ebc07d?q=80&w=1200&auto=format&fit=crop',
        'projects': [
            {
                'name': 'Qrobt 虛擬導遊',
                'description': '可愛的機器人導覽員會出現在您的手機螢幕上，帶領您遊覽各個私房景點，了解水井村歷史。',
                'img_url': 'https://images.unsplash.com/photo-1546776310-eef45dd6d63c?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': '地方故事 QR 全紀錄',
                'description': '在客棧各處設有互動連結，遊客可自行探索關於「三寶奇緣」與在地耕耘的神祕小故事。',
                'img_url': 'https://images.unsplash.com/photo-1532153322677-1cbf00d0865.jpg?q=80&w=600&auto=format&fit=crop'
            }
        ]
    }
]

for idx, sec in enumerate(tech_sections_data):
    section, created = TechSection.objects.get_or_create(
        title=sec['title'],
        defaults={'intro_text': sec['intro_text'], 'layout_type': sec['layout_type'], 'order': idx}
    )
    if not created:
        section.intro_text = sec['intro_text']
        section.layout_type = sec['layout_type']
        section.order = idx
    
    if not section.image:
        img_file = download_image(sec['img_url'], 'tech_sections', f"sec_{idx}.jpg")
        if img_file:
            section.image.save(f"sec_{idx}.jpg", img_file, save=False)
    section.save()
    
    for p_idx, p in enumerate(sec['projects']):
        project, p_created = TechProject.objects.get_or_create(
            name=p['name'], 
            section=section,
            defaults={'description': p['description'], 'order': p_idx}
        )
        if not p_created:
            project.description = p['description']
            project.order = p_idx
        
        if not project.image:
            img_file = download_image(p['img_url'], 'tech', f"proj_{idx}_{p_idx}.jpg")
            if img_file:
                project.image.save(f"proj_{idx}_{p_idx}.jpg", img_file, save=False)
        project.save()

print("--- Seeding Stories, Achievements & Workshops ---")
# Stories
for s in [
    {'title': '水井村：從鹽份地帶到智慧聚落', 'cat': 'local', 'url': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?q=80&w=800&auto=format&fit=crop'},
    {'title': '院長領軍：許永和教授的在地實踐', 'cat': 'usr', 'url': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=800&auto=format&fit=crop'}
]:
    story, created = Story.objects.get_or_create(
        title=s['title'],
        defaults={'category': s['cat'], 'content': f"<p>關於{s['title']}的精彩內容...</p>"}
    )
    if not created:
        story.category = s['cat']
    
    if not story.image:
        img_file = download_image(s['url'], 'stories', f"{s['cat']}.jpg")
        if img_file:
            story.image.save(f"{s['cat']}.jpg", img_file, save=False)
    story.save()

# Achievements
ach_data = {
    'type': 'news',
    'summary': '虎科大團隊聯手水井村，展現節水技術與減碳成果，榮獲年度永續獎項肯定。',
    'date': datetime.date.today(),
}
ach, created = USRAchievement.objects.get_or_create(
    title='2026 海洋科學節得獎報導',
    defaults=ach_data
)
if not created:
    for key, value in ach_data.items():
        setattr(ach, key, value)

if not ach.image:
    img_file = download_image('https://images.unsplash.com/photo-1531297484001-80022131f5a1?q=80&w=800&auto=format&fit=crop', 'achievements', 'award.jpg')
    if img_file:
        ach.image.save('award.jpg', img_file, save=False)
ach.save()

# Workshops
for w in [
    {'name': '不蒜花手作課', 'cat': '農廢藝術', 'url': 'https://images.unsplash.com/photo-1490750967868-886cde7471fb?q=80&w=800&auto=format&fit=crop'},
    {'name': '智慧機器人組裝', 'cat': '科技教育', 'url': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=800&auto=format&fit=crop'}
]:
    work, created = ExperienceCourse.objects.get_or_create(
        name=w['name'],
        defaults={'category': w['cat'], 'description': f"親手體驗{w['name']}的魅力，感受在地與科技的連結。"}
    )
    if not created:
        work.category = w['cat']
        work.description = f"親手體驗{w['name']}的魅力，感受在地與科技的連結。"
    
    if not work.image:
        img_file = download_image(w['url'], 'workshops', f"{w['name']}.jpg")
        if img_file:
            work.image.save(f"{w['name']}.jpg", img_file, save=False)
    work.save()

print("All system portals and expansion data seeded successfully!")
