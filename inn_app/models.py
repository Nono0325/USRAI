from django.db import models
import uuid
from tinymce.models import HTMLField
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
import subprocess
import re
class CarouselItem(models.Model):
    title = models.CharField('標題', max_length=100)
    subtitle = models.CharField('副標題', max_length=200, blank=True)
    image = models.FileField('圖片', upload_to='carousel/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    order = models.IntegerField('排序', default=0)
    show_title = models.BooleanField('顯示標題', default=True)
    show_subtitle = models.BooleanField('顯示副標題', default=True)
    is_active = models.BooleanField('上架狀態', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = '輪播圖'
        verbose_name_plural = '輪播圖'

    def __str__(self):
        return self.title

class Service(models.Model):
    title = models.CharField('服務名稱', max_length=100)
    description = HTMLField('服務說明')
    image = models.FileField('圖片', upload_to='services/', null=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    is_active = models.BooleanField('啟用', default=True)

    class Meta:
        verbose_name = '三生共好服務'
        verbose_name_plural = '三生共好服務'

    def __str__(self):
        return self.title

class DutyStaff(models.Model):
    name = models.CharField('姓名', max_length=50)
    role = models.CharField('職稱', max_length=50)
    contact = models.CharField('聯絡方式', max_length=100, blank=True)
    is_on_duty = models.BooleanField('目前是否值班', default=False)

    class Meta:
        verbose_name = '值班人員'
        verbose_name_plural = '值班人員'

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField('課程名稱', max_length=100)
    instructor = models.CharField('講師', max_length=100)
    description = HTMLField('課程介紹')
    image = models.FileField('課程封面', upload_to='courses/', null=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    capacity = models.IntegerField('名額限制')
    reg_start_time = models.DateTimeField('報名開始時間', null=True, blank=True)
    reg_end_time = models.DateTimeField('報名截止時間', null=True, blank=True)
    start_time = models.DateTimeField('開課時間')
    end_time = models.DateTimeField('結束時間', null=True, blank=True)
    includes_lunch = models.BooleanField('是否提供午餐', default=False)
    recommended_age = models.CharField('建議年齡', max_length=50, blank=True, help_text='例如：7歲以上、不限')
    requires_computer = models.BooleanField('自備電腦', default=False)
    is_active = models.BooleanField('開放報名', default=True)

    class Meta:
        verbose_name = '課程'
        verbose_name_plural = '課程'

    def __str__(self):
        return self.title

class Registration(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='報名課程')
    name = models.CharField('姓名', max_length=50)
    phone = models.CharField('電話', max_length=20)
    email = models.EmailField('Email')
    
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他/不提供'),
    ]
    gender = models.CharField('性別', max_length=10, choices=GENDER_CHOICES, default='M')
    headcount = models.IntegerField('報名人數', default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    is_waitlisted = models.BooleanField('排入候補', default=False)
    is_attended = models.BooleanField('已報到', default=False)
    attended_at = models.DateTimeField('報到時間', null=True, blank=True)
    checkin_token = models.UUIDField('掃碼憑證', default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField('報名時間', auto_now_add=True)

    @property
    def waitlist_number(self):
        if not self.is_waitlisted:
            return None
        # 尋找同一堂課、也是候補，且報名時間早於目前這筆紀錄的數量
        return Registration.objects.filter(
            course=self.course,
            is_waitlisted=True,
            created_at__lt=self.created_at
        ).count() + 1

    class Meta:
        verbose_name = '報名紀錄'
        verbose_name_plural = '報名紀錄'

    def __str__(self):
        return f'{self.name} - {self.course.title}'

class SigninTemplate(models.Model):
    name = models.CharField('範本名稱', max_length=100)
    file = models.FileField('Word 範本檔案', upload_to='templates/', help_text='請上傳含有 docxtpl 標籤的 .docx 檔案。')
    is_default = models.BooleanField('預設選項', default=False)
    created_at = models.DateTimeField('建立時間', auto_now_add=True)

    class Meta:
        verbose_name = '簽到表版型範本'
        verbose_name_plural = '簽到表版型範本'

    def __str__(self):
        return f"{self.name} {'(預設)' if self.is_default else ''}"
        
    def save(self, *args, **kwargs):
        if self.is_default:
            SigninTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

class Event(models.Model):
    title = models.CharField('活動標題', max_length=100)
    description = models.TextField('活動描述')
    date = models.DateField('活動日期')

    class Meta:
        verbose_name = '活動'
        verbose_name_plural = '活動'
        ordering = ['-date']

    def __str__(self):
        return self.title

class Story(models.Model):
    STORY_CATEGORIES = [
        ('local', '在地故事'),
        ('usr', 'USR 努力過程'),
        ('achievement', '師生表現'),
    ]
    title = models.CharField('標題', max_length=200)
    category = models.CharField('分類', max_length=20, choices=STORY_CATEGORIES)
    content = HTMLField('內容')
    image = models.FileField('封面圖', upload_to='stories/', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    created_at = models.DateTimeField('發布時間', auto_now_add=True)

    class Meta:
        verbose_name = '故事牆'
        verbose_name_plural = '故事牆'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

class USRAchievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('news', '新聞報導'),
        ('video', '影片成果'),
        ('display', '成果展示'),
    ]
    title = models.CharField('成果標題', max_length=200)
    type = models.CharField('類型', max_length=20, choices=ACHIEVEMENT_TYPES)
    summary = models.TextField('簡介')
    external_link = models.URLField('外部連結', blank=True, null=True, help_text='例如：影片網址或新聞連結')
    image = models.FileField('代表圖', upload_to='achievements/', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    date = models.DateField('日期')

    class Meta:
        verbose_name = 'USR成果'
        verbose_name_plural = 'USR成果'
        ordering = ['-date']

    def __str__(self):
        return self.title

class TechSection(models.Model):
    title = models.CharField('區塊標題', max_length=100)
    intro_text = HTMLField('前言/簡介', blank=True)
    image = models.FileField('側邊圖片', upload_to='tech_sections/', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    LAYOUT_CHOICES = [
        ('side_image', '左圖右卡片 (AIoT 樣式)'),
        ('side_text', '左文右方塊 (AR 樣式)'),
    ]
    layout_type = models.CharField('排版樣式', max_length=20, choices=LAYOUT_CHOICES, default='side_image')
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('啟用', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = '科技專案區塊'
        verbose_name_plural = '科技專案區塊'

    def __str__(self):
        return self.title

class TechProject(models.Model):
    section = models.ForeignKey(TechSection, on_delete=models.CASCADE, related_name='projects', verbose_name='所屬區塊', null=True, blank=True)
    name = models.CharField('專案名稱', max_length=100)
    type = models.CharField('技術類型 (舊版)', max_length=20, choices=[('aiot', 'AIoT 應用'), ('ar_interact', 'AR/互動導覽')], blank=True)
    description = HTMLField('技術細節說明')
    image = models.FileField('示意圖', upload_to='tech/', null=True, blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    order = models.IntegerField('排序', default=0)
    is_active = models.BooleanField('啟用', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = '科技特色項目'
        verbose_name_plural = '科技特色項目'

    def __str__(self):
        return self.name

class ExperienceCourse(models.Model):
    name = models.CharField('課程名稱', max_length=100)
    description = models.TextField('課程簡介')
    category = models.CharField('分類', max_length=50, help_text='例如：不蒜花、機器人')
    image = models.FileField('課程圖示', upload_to='workshops/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'mov'])])
    
    class Meta:
        verbose_name = '活動體驗課程說明'
        verbose_name_plural = '活動體驗課程說明'

    def __str__(self):
        return self.name

class ContactInfo(models.Model):
    title = models.CharField('頁面標題', max_length=100, default='聯絡我們')
    intro_text = models.TextField('前言簡介', default='有任何問題或是想要預約特別活動嗎？歡迎隨時與我們聯繫！我們會盡快回覆您。')
    address = models.CharField('地址', max_length=200, default='桃園市水井村風雲街 8 號')
    phone = models.CharField('電話', max_length=50, default='(03) 1234-5678')
    email = models.EmailField('電子郵件', default='service@fengyuninn.com')
    map_iframe = models.TextField('Google Map 嵌入語法', blank=True, help_text='請貼上 Google Maps 分享的 iframe 語法')
    is_active = models.BooleanField('啟用', default=True)

    class Meta:
        verbose_name = '聯絡資訊設定'
        verbose_name_plural = '聯絡資訊設定'

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField('姓名', max_length=100)
    phone = models.CharField('電話', max_length=50)
    email = models.EmailField('Email')
    message = models.TextField('訊息內容')
    created_at = models.DateTimeField('收件時間', auto_now_add=True)

    class Meta:
        verbose_name = '聯絡訊息收件夾'
        verbose_name_plural = '聯絡訊息收件夾'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

class LoginRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='登入者', null=True, blank=True)
    username = models.CharField('使用者名稱', max_length=150, blank=True)
    ip_address = models.GenericIPAddressField('IP 地址', null=True, blank=True)
    mac_address = models.CharField('MAC 地址', max_length=50, null=True, blank=True)
    user_agent = models.CharField('瀏覽器/裝置', max_length=255, null=True, blank=True)
    login_time = models.DateTimeField('登入時間', auto_now_add=True)

    class Meta:
        verbose_name = '登入紀錄'
        verbose_name_plural = '登入紀錄'
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.username} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"

def get_mac_address_from_ip(ip):
    if not ip or ip == '127.0.0.1':
        import uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        return mac
    try:
        # For Windows
        pid = subprocess.Popen(["arp", "-a", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        s, _ = pid.communicate()
        s = s.decode("big5", errors='ignore') # Windows big5/cp950 output
        mac = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", s)
        if mac:
            return mac.group(0).replace('-', ':')
        
        # For Linux
        pid2 = subprocess.Popen(["arp", "-n", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        s2, _ = pid2.communicate()
        s2 = s2.decode("utf-8", errors='ignore')
        mac2 = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s2)
        if mac2:
            return mac2.group(0)
    except Exception:
        pass
    return "無法取得 (非區域網路)"

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def record_login(sender, user, request, **kwargs):
    ip = get_client_ip(request)
    mac = get_mac_address_from_ip(ip)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]
    LoginRecord.objects.create(
        user=user,
        username=user.username,
        ip_address=ip,
        mac_address=mac,
        user_agent=user_agent
    )
