# authentication/urls.py
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # General authentication
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Login selection page
    path('login/', views.LoginSelectionView.as_view(), name='login_selection'),
    
    # Separate login pages for each user type
    path('student/login/', views.StudentLoginView.as_view(), name='student_login'),
    path('admin/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('institution/login/', views.InstitutionLoginView.as_view(), name='institution_login'),
    
    # Backward compatibility
    path('login-old/', views.LoginView.as_view(), name='login'),
]