# institution/urls.py
from django.urls import path
from . import views

app_name = 'institution'

urlpatterns = [
    path('dashboard/', views.InstitutionDashboardView.as_view(), name='dashboard'),
    path('courses/', views.CourseListView.as_view(), name='courses'),
    path('students/', views.AdmittedStudentsView.as_view(), name='students'),
    path('seat-matrix/', views.SeatMatrixView.as_view(), name='seat_matrix'),
]