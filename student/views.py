# student/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .models import StudentProfile, Application, StudentDocument, CETScore, SeatAllotment
from .forms import StudentProfileForm, ApplicationForm, DocumentUploadForm

class StudentRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'student'

class StudentDashboardView(StudentRequiredMixin, TemplateView):
    template_name = 'student/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student_profile = self.request.user.student_profile
            context.update({
                'student_profile': student_profile,
                'application': getattr(student_profile, 'application', None),
                'cet_score': getattr(student_profile, 'cet_score', None),
                'documents': student_profile.documents.all(),
                'allotments': student_profile.allotments.all(),
            })
        except StudentProfile.DoesNotExist:
            context['needs_profile'] = True
        return context

class StudentProfileView(StudentRequiredMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = 'student/profile.html'
    success_url = reverse_lazy('student:dashboard')
    
    def get_object(self):
        try:
            return StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
            # Return a new instance without saving it
            return StudentProfile(user=self.request.user)
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class ApplicationView(StudentRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = 'student/application.html'
    success_url = reverse_lazy('student:dashboard')
    
    def get_object(self):
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        application, created = Application.objects.get_or_create(student=student_profile)
        return application
    
    def form_valid(self, form):
        form.instance.student = get_object_or_404(StudentProfile, user=self.request.user)
        
        if 'submit' in self.request.POST:
            # Check if profile is complete before submission
            if not form.instance.student.date_of_birth:
                messages.error(self.request, 'Please complete your profile before submitting the application.')
                return self.form_invalid(form)
            
            form.instance.submit_application()
            messages.success(self.request, 'Application submitted successfully!')
        else:
            messages.success(self.request, 'Application saved as draft.')
        return super().form_valid(form)

class DocumentUploadView(StudentRequiredMixin, TemplateView):
    template_name = 'student/documents.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        context.update({
            'student_profile': student_profile,
            'documents': student_profile.documents.all(),
            'form': DocumentUploadForm(),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        form = DocumentUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student_profile
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('student:documents')
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(request, self.template_name, context)

class VerifyDocumentView(StudentRequiredMixin, TemplateView):
    def post(self, request, doc_id):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        document = get_object_or_404(StudentDocument, id=doc_id, student=student_profile)
        
        # Run mock AI verification
        document.verify_document()
        
        if document.verification_status == 'verified':
            messages.success(request, f'Document {document.document_type} verified successfully!')
        else:
            messages.warning(request, f'Document {document.document_type} verification failed. Please reupload.')
        
        return redirect('student:documents')

class CETScoreView(StudentRequiredMixin, TemplateView):
    template_name = 'student/scores.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student_profile = self.request.user.student_profile
            context['cet_score'] = getattr(student_profile, 'cet_score', None)
        except StudentProfile.DoesNotExist:
            pass
        return context

class CounselingView(StudentRequiredMixin, TemplateView):
    template_name = 'student/counseling.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student_profile = self.request.user.student_profile
            context.update({
                'student_profile': student_profile,
                'allotments': student_profile.allotments.all(),
            })
        except StudentProfile.DoesNotExist:
            pass
        return context

class AllotmentView(StudentRequiredMixin, TemplateView):
    template_name = 'student/allotment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student_profile = self.request.user.student_profile
            context.update({
                'allotments': student_profile.allotments.all(),
                'latest_allotment': student_profile.allotments.first(),
            })
        except StudentProfile.DoesNotExist:
            pass
        return context

class AcceptSeatView(StudentRequiredMixin, TemplateView):
    def post(self, request, allotment_id):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        allotment = get_object_or_404(SeatAllotment, id=allotment_id, student=student_profile)
        
        allotment.accept_seat()
        messages.success(request, f'Congratulations! You have accepted the seat for {allotment.allotted_course} at {allotment.allotted_institution.name}')
        
        return redirect('student:allotment')