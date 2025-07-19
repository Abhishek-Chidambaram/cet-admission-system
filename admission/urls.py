# admission/urls.py
from django.urls import path
from . import views

app_name = 'admission'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('system-admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('system-admin/students/', views.StudentListView.as_view(), name='student_list'),
    path('system-admin/institutions/', views.InstitutionListView.as_view(), name='institution_list'),
    path('system-admin/counseling/', views.CounselingManagementView.as_view(), name='counseling_management'),
    path('system-admin/generate-scores/', views.GenerateScoresView.as_view(), name='generate_scores'),
    path('system-admin/run-counseling/', views.RunCounselingView.as_view(), name='run_counseling'),
    path('results/', views.ResultsView.as_view(), name='results'),
]