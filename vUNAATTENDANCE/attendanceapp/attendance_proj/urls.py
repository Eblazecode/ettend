
from django.urls import path
from . import views
import os
from django.conf import settings    
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('student', views.student, name='student'),
    path('admin', views.admin, name='admin'),
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('success/', views.success_url, name='success_url'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('time_table/', views.upload_DAP_timetable, name='time_table'),
    path('admin_register/', views.admin_register, name='admin_register'),  # Example of adding a new URL pattern
    path('view_timetable/', views.view_timetable, name='view_timetable'),
    path('upload_machine_attendance/',views.machine_attendance_upload, name='machine_attendance'),    
    path('view_machine_attendance/',views.machine_upload_view, name='upload_view'),
    path('student_attendance/',views.generate_attendance, name='student_attendance'),
    path('get-courses/<str:department>/', views.get_courses, name='get_courses'),
    path('process-selection/', views.process_selection, name='process_selection'),
    path('unschduled_attendance/', views.unscheduled_events_attendance, name='unscheduled_attendance'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('summary_attendance', views.summary_attendance, name='summary_attend'),
    path('track_attendance/', views.track_attendance, name='track_attendance'),
    path('upload_registered_students/', views.Update_weekely_attendance_DB, name='dept_upload'),
    path('score_card/', views.attendance_score_card, name='scorecard'),


]
# Compare this snippet from attendanceapp/attendance_proj/forms.py: 