# student/urls.py
from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('dashboard/', views.StudentDashboardView.as_view(), name='dashboard'),
    path('profile/', views.StudentProfileView.as_view(), name='profile'),
    path('application/', views.ApplicationView.as_view(), name='application'),
    path('documents/', views.DocumentUploadView.as_view(), name='documents'),
    path('documents/verify/<int:doc_id>/', views.VerifyDocumentView.as_view(), name='verify_document'),
    path('scores/', views.CETScoreView.as_view(), name='scores'),
    path('counseling/', views.CounselingView.as_view(), name='counseling'),
    path('allotment/', views.AllotmentView.as_view(), name='allotment'),
    path('accept-seat/<int:allotment_id>/', views.AcceptSeatView.as_view(), name='accept_seat'),
]