from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from datetime import timedelta
from django.utils.dateformat import format
from .models import CarouselItem, Service, DutyStaff, Course, Registration, Event, Story, USRAchievement, TechProject, ExperienceCourse, TechSection, ContactInfo, ContactMessage
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import RegistrationForm

def home(request):
    carousels = CarouselItem.objects.filter(is_active=True).order_by('order')
    services = Service.objects.filter(is_active=True)
    duty_staffs = DutyStaff.objects.filter(is_on_duty=True)
    
    # 門戶平台展示內容 (Portal Sections)
    latest_stories = Story.objects.all()[:3]
    latest_achievements = USRAchievement.objects.all()[:3]
    tech_projects = TechProject.objects.filter(is_active=True)[:4]
    
    return render(request, 'inn_app/home.html', {
        'carousels': carousels,
        'services': services,
        'duty_staffs': duty_staffs,
        'latest_stories': latest_stories,
        'latest_achievements': latest_achievements,
        'tech_projects': tech_projects
    })

def course_list(request):
    courses = Course.objects.filter(is_active=True).order_by('-start_time')
    return render(request, 'inn_app/course_list.html', {'courses': courses})

def course_detail(request, course_id):
    from django.utils import timezone
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # 時效與狀態過濾器 (初始化狀態)
    now = timezone.now()
    is_reg_open = True
    reg_status_msg = ""
    context_error_msg = [] # 用來存放要顯示在 Modal 中的錯誤訊息列表
    
    if course.reg_start_time and now < course.reg_start_time:
        is_reg_open = False
        reg_status_msg = "報名尚未開放"
    elif course.reg_end_time and now > course.reg_end_time:
        is_reg_open = False
        reg_status_msg = "報名已截止"
        
    from django.db.models import Sum
    current_regs = Registration.objects.filter(course=course, is_waitlisted=False).aggregate(total=Sum('headcount'))['total'] or 0
    # [公平性優化] 若已有候補名單，則該課程對外應維持「額滿」狀態，防止新訪客插隊
    has_waitlist = Registration.objects.filter(course=course, is_waitlisted=True).exists()
    is_full = (current_regs >= course.capacity) or has_waitlist

    if request.method == 'POST':
        # 把接收到的資料送入表單過濾器
        form = RegistrationForm(request.POST, course_instance=course)
        
        # Check time
        if not is_reg_open:
            msg = f'無法進行報名：{reg_status_msg}'
            messages.error(request, msg)
            # 將錯誤存入 session，以便在 Redirect 後也能觸發 Error Modal
            request.session['error_modal_msg'] = [msg]
            return redirect('inn_app:course_detail', course_id=course.id)
            
        if form.is_valid():
            from django.db.models import Sum
            current_registrations = Registration.objects.filter(course=course, is_waitlisted=False).aggregate(total=Sum('headcount'))['total'] or 0
            # [公平性檢核] 同步檢查是否有候補者在排隊
            waitlist_exists = Registration.objects.filter(course=course, is_waitlisted=True).exists()
            
            registration = form.save(commit=False)
            registration.course = course
            
            requested = registration.headcount
            from django.core.mail import send_mail
            
            if (current_registrations + requested > course.capacity) or waitlist_exists:
                # [候補機制] 額滿或已有候補則轉為候補單
                registration.is_waitlisted = True
                registration.save()
                messages.warning(request, f'⚠️ 正常名額已滿，您已成功排入候補名單（目前為候補第 {registration.waitlist_number} 號）！若有民眾取消釋出名額，我們將第一時間與您聯繫。')
                send_mail(
                    f'【水井村風雲客棧】候補通知：{course.title}',
                    f'{registration.name} 您好：\n\n您已成功排入 {course.title} 的候補名單，順位為第 {registration.waitlist_number} 號。\n若有釋出名額我們將主動與您聯繫，謝謝！',
                    'noreply@fengyuninn.com',
                    [registration.email],
                    fail_silently=True,
                )
                # Store waitlist info in session
                request.session['show_waitlist_modal'] = True
                request.session['waitlist_num'] = registration.waitlist_number
                request.session['reg_name'] = registration.name
                request.session['reg_course'] = course.title
            else:
                # [正取機制]
                registration.save()
                messages.success(request, '✅ 報名成功！我們已發送確認通知信至您的信箱，現場報到請出示專屬 QR 條碼。')
                checkin_url = request.build_absolute_uri(reverse('inn_app:check_in_scan', args=[str(registration.checkin_token)]))
                send_mail(
                    f'【水井村風雲客棧】報名成功通知：{course.title}',
                    f'{registration.name} 您好：\n\n恭喜您已成功報名！\n- 參與課程：{course.title}\n- 報名人數：{registration.headcount} 人\n\n【您的專屬QR報到憑證】（請保存此網址或截圖供現場工作人員掃描）\n{checkin_url}\n\n期待與您在客棧相見！',
                    'noreply@fengyuninn.com',
                    [registration.email],
                    fail_silently=True,
                )
                
                # Store data in session for the popup modal after redirect
                request.session['show_qr_modal'] = True
                request.session['reg_token'] = str(registration.checkin_token)
                request.session['reg_name'] = registration.name
                request.session['reg_course'] = course.title
                
            return redirect('inn_app:course_detail', course_id=course.id)
        else:
            # Collect errors for the modal
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
                    context_error_msg.append(error)
                    
    # Generate Google Calendar URL
    from urllib.parse import quote
    end_time = course.end_time if course.end_time else course.start_time + timedelta(hours=2)
    dtstart = format(course.start_time, 'Ymd\\THis')
    dtend = format(end_time, 'Ymd\\THis')
    gcal_url = (
        f"https://calendar.google.com/calendar/render?action=TEMPLATE"
        f"&text={quote(course.title)}&dates={dtstart}/{dtend}"
        f"&details={quote(course.description)}&location={quote('水井村風雲客棧')}"
    )
    
    # Check for modal session data (Popping data passed via redirect)
    show_qr_modal = request.session.pop('show_qr_modal', False)
    reg_token = request.session.pop('reg_token', None)
    reg_name = request.session.pop('reg_name', None)
    reg_course = request.session.pop('reg_course', None)
    
    show_waitlist_modal = request.session.pop('show_waitlist_modal', False)
    waitlist_num = request.session.pop('waitlist_num', None)
    
    # 若 session 中有預存的錯誤訊息 (多位在 Redirect 後讀取)
    session_errors = request.session.pop('error_modal_msg', [])
    if session_errors:
        context_error_msg.extend(session_errors)
        
    return render(request, 'inn_app/course_detail.html', {
        'course': course, 
        'gcal_url': gcal_url,
        'is_reg_open': is_reg_open,
        'reg_status_msg': reg_status_msg,
        'is_full': is_full,
        'show_qr_modal': show_qr_modal,
        'reg_token': reg_token,
        'reg_name': reg_name,
        'reg_course': reg_course,
        'show_waitlist_modal': show_waitlist_modal,
        'waitlist_num': waitlist_num,
        'error_modal_msg': context_error_msg if context_error_msg else None
    })

def duty_staff(request):
    staffs = DutyStaff.objects.all().order_by('-is_on_duty')
    return render(request, 'inn_app/duty_staff.html', {'staffs': staffs})

def calendar_view(request):
    return render(request, 'inn_app/calendar.html')

def course_events_api(request):
    courses = Course.objects.filter(is_active=True)
    events = []
    for c in courses:
        end_time = c.end_time if c.end_time else c.start_time + timedelta(hours=2)
        events.append({
            'id': c.id,
            'title': f"🎓[上課] {c.title}",
            'start': c.start_time.isoformat(),
            'end': end_time.isoformat(),
            'url': reverse('inn_app:course_detail', args=[c.id]),
            'color': '#5D4037'
        })
        
        # 將報名時間也加為行事曆上的事件（綠色標籤）
        if c.reg_start_time and c.reg_end_time:
            events.append({
                'id': f"reg-{c.id}",
                'title': f"📝[報名開放] {c.title}",
                'start': c.reg_start_time.isoformat(),
                'end': c.reg_end_time.isoformat(),
                'url': reverse('inn_app:course_detail', args=[c.id]),
                'color': '#2E8B57'
            })
    return JsonResponse(events, safe=False)

def download_ics(request, course_id):
    course = get_object_or_404(Course, id=course_id, is_active=True)
    end_time = course.end_time if course.end_time else course.start_time + timedelta(hours=2)
    
    dtstart = format(course.start_time, 'Ymd\\THis')
    dtend = format(end_time, 'Ymd\\THis')
    desc = course.description.replace('\n', '\\n').replace('\r', '')
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//FengYunInn//NONSGML v1.0//EN
BEGIN:VEVENT
UID:course-{course.id}@fengyuninn.com
DTSTAMP:{dtstart}
DTSTART;TZID=Asia/Taipei:{dtstart}
DTEND;TZID=Asia/Taipei:{dtend}
SUMMARY:{course.title}
DESCRIPTION:{desc}
LOCATION:水井村風雲客棧
END:VEVENT
END:VCALENDAR"""
    
    response = HttpResponse(ics_content, content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="course_{course.id}.ics"'
    return response

def my_bookings(request):
    registrations = None
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        if phone and email:
            registrations = Registration.objects.filter(phone=phone, email=email).select_related('course').order_by('-created_at')
            if not registrations.exists():
                messages.error(request, '❌ 找不到相符的報名紀錄，請確認電話與 Email 是否完全正確（過去無填寫 Email 的紀錄將無法被查詢）。')
            else:
                messages.success(request, '✅ 查詢成功！以下是您的報名紀錄。')
        else:
            messages.error(request, '❌ 請確認已經輸入【聯絡電話】與【Email】再送出查詢。')
            
    return render(request, 'inn_app/my_bookings.html', {'registrations': registrations})

def cancel_booking(request, reg_id):
    if request.method == 'POST':
        registration = get_object_or_404(Registration, id=reg_id)
        
        # [加固身分驗證] 核對取消者的電話與 Email 是否與紀錄相符，防止 IDOR 橫向越權刪除
        phone = request.POST.get('confirm_phone', '').strip()
        email = request.POST.get('confirm_email', '').strip()
        
        if phone == registration.phone and email == registration.email:
            course_title = registration.course.title
            is_wait = registration.is_waitlisted
            registration.delete()
            if is_wait:
                messages.success(request, f'✅ 已取消【{course_title}】的候補登記！')
            else:
                messages.success(request, f'✅ 已成功取消【{course_title}】的報名紀錄！該名額已經重新釋出。')
        else:
            # 即使是在本地，也要防止惡意 ID 掃描
            messages.error(request, '❌ 身分驗證失敗，無法取消報名。請確保您是從本人查詢頁面進入操作。')
            
    return redirect('inn_app:home')

def check_in_scan(request, token):
    if not request.user.is_staff:
        from django.contrib.auth.views import redirect_to_login
        # 沒有權限的手機一掃描，直接被踢去登入畫面
        return redirect_to_login(request.get_full_path())
        
    registration = get_object_or_404(Registration, checkin_token=token)
    
    if registration.is_attended:
        messages.warning(request, f"⚠️ 【{registration.name}】（共 {registration.headcount} 人）稍早已經報到過了喔！請勿重複核銷。")
    else:
        from django.utils import timezone
        registration.is_attended = True
        registration.attended_at = timezone.now()
        registration.save()
        messages.success(request, f"🎉 掃碼核銷成功！【{registration.name}】（共 {registration.headcount} 人）已成功登記入場。")
        
    return redirect('inn_app:home')

def about(request):
    return render(request, 'inn_app/about.html')

def event_list(request):
    query = request.GET.get('q', '')
    events = Event.objects.all().order_by('-date')
    
    if query:
        events = events.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    
    paginator = Paginator(events, 6) # 6 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inn_app/event_list.html', {
        'page_obj': page_obj,
        'query': query
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'inn_app/event_detail.html', {'event': event})

def contact(request):
    contact_info = ContactInfo.objects.filter(is_active=True).first()
    if request.method == 'POST':
        # [資安加固] 加入輸入長度限制，防止資料庫洪水攻擊
        name = request.POST.get('name', '')[:100].strip()
        phone = request.POST.get('phone', '')[:50].strip()
        email = request.POST.get('email', '')[:150].strip()
        message = request.POST.get('message', '')[:5000].strip()
        
        if not name or not message:
            messages.error(request, '請確認已經填寫完整的姓名與訊息內容。')
            return redirect('inn_app:contact')
            
        # Save to database
        ContactMessage.objects.create(
            name=name,
            phone=phone,
            email=email,
            message=message
        )
        
        messages.success(request, '感謝您的訊息！我們將盡快與您聯絡。')
        return redirect('inn_app:contact')
        
    return render(request, 'inn_app/contact.html', {'contact_info': contact_info})

def story_list(request):
    cat = request.GET.get('cat')
    stories = Story.objects.all()
    if cat:
        stories = stories.filter(category=cat)
    
    paginator = Paginator(stories, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inn_app/story_list.html', {
        'page_obj': page_obj,
        'active_cat': cat
    })

def story_detail(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    return render(request, 'inn_app/story_detail.html', {'story': story})

def usr_showcase(request):
    achievements = USRAchievement.objects.all()
    return render(request, 'inn_app/usr_showcase.html', {'achievements': achievements})

def aiot_guide(request):
    sections = TechSection.objects.filter(is_active=True).prefetch_related('projects')
    return render(request, 'inn_app/aiot_guide.html', {'sections': sections})

def workshop_list(request):
    workshops = ExperienceCourse.objects.all()
    return render(request, 'inn_app/workshop_list.html', {'workshops': workshops})

def search(request):
    query = request.GET.get('q', '').strip()
    results = {
        'stories': [],
        'courses': [],
        'events': [],
        'achievements': [],
        'tech_projects': [],
        'workshops': []
    }
    
    if query:
        # Search Stories
        results['stories'] = Story.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        
        # Search Courses (Title, Description, Instructor)
        results['courses'] = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(instructor__icontains=query)
        )
        
        # Search Events
        results['events'] = Event.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        
        # Search USR Achievements (Title, Summary)
        results['achievements'] = USRAchievement.objects.filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )
        
        # Search Tech Projects
        results['tech_projects'] = TechProject.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
        
        # Search Workshops
        results['workshops'] = ExperienceCourse.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Calculate total count
    total_count = sum(len(list(v)) for v in results.values())
    
    return render(request, 'inn_app/search_results.html', {
        'query': query,
        'results': results,
        'total_count': total_count
    })
