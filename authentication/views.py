# authentication/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import User
from .forms import UserRegistrationForm, UserProfileForm, CustomAuthenticationForm

class LoginView(DjangoLoginView):
    template_name = 'authentication/login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        user = self.request.user
        if user.user_type == 'student':
            return reverse_lazy('student:dashboard')
        elif user.user_type == 'institution':
            return reverse_lazy('institution:dashboard')
        elif user.user_type == 'admin':
            return reverse_lazy('admission:admin_dashboard')
        return reverse_lazy('admission:home')

class StudentLoginView(DjangoLoginView):
    template_name = 'authentication/student_login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('student:dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if user.user_type != 'student':
            form.add_error(None, 'This login is only for students. Please use the correct login page.')
            return self.form_invalid(form)
        return super().form_valid(form)

class AdminLoginView(DjangoLoginView):
    template_name = 'authentication/admin_login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('admission:admin_dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if user.user_type != 'admin':
            form.add_error(None, 'This login is only for administrators. Please use the correct login page.')
            return self.form_invalid(form)
        return super().form_valid(form)

class InstitutionLoginView(DjangoLoginView):
    template_name = 'authentication/institution_login.html'
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('institution:dashboard')
    
    def form_valid(self, form):
        user = form.get_user()
        if user.user_type != 'institution':
            form.add_error(None, 'This login is only for institutions. Please use the correct login page.')
            return self.form_invalid(form)
        return super().form_valid(form)

class LoginSelectionView(TemplateView):
    template_name = 'authentication/login_selection.html'

class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('admission:home')

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('authentication:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please login.')
        return response

class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'authentication/profile.html'
    success_url = reverse_lazy('authentication:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)