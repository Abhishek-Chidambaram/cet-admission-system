from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('plans/', views.plans_view, name='plans'),
]
