from django.urls import path
from . import views

app_name = 'inn_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/download.ics', views.download_ics, name='download_ics'),
    path('duty-staff/', views.duty_staff, name='duty_staff'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/courses/events/', views.course_events_api, name='course_events_api'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:reg_id>/', views.cancel_booking, name='cancel_booking'),
    path('check-in/<uuid:token>/', views.check_in_scan, name='check_in_scan'),
    path('about/', views.about, name='about'),
    path('events/', views.event_list, name='event_list'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('contact/', views.contact, name='contact'),
    path('stories/', views.story_list, name='story_list'),
    path('story/<int:story_id>/', views.story_detail, name='story_detail'),
    path('usr-showcase/', views.usr_showcase, name='usr_showcase'),
    path('aiot-guide/', views.aiot_guide, name='aiot_guide'),
    path('workshops/', views.workshop_list, name='workshop_list'),
    path('search/', views.search, name='search'),
]
