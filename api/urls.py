# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'institutions', views.InstitutionViewSet)
router.register(r'applications', views.ApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('mock-notification/', views.MockNotificationView.as_view(), name='mock_notification'),
    path('mock-payment/', views.MockPaymentView.as_view(), name='mock_payment'),
]