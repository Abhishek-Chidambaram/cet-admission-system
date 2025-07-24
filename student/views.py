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
    
    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(self.request, 'Access denied. Student login required.')
        return redirect('authentication:student_login')

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
            # Create and return a new profile instance
            profile = StudentProfile(user=self.request.user)
            return profile
    
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
        try:
            student_profile = StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
            # Redirect to profile creation if profile doesn't exist
            messages.error(self.request, 'Please complete your profile first before applying.')
            return None
        
        application, created = Application.objects.get_or_create(student=student_profile)
        return application
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add institutions and courses data for dynamic selection
        from institution.models import Institution, Course
        import json
        
        institutions = Institution.objects.filter(is_active=True).order_by('name')
        courses_data = {}
        
        for institution in institutions:
            courses = Course.objects.filter(
                institution=institution, 
                is_active=True
            ).order_by('course_name')
            courses_data[str(institution.id)] = [
                {
                    'value': f"{institution.code}_{course.course_code}",
                    'name': course.course_name,
                    'code': course.course_code
                }
                for course in courses
            ]
        
        # Only pass valid preferences (properly formatted strings)
        current_prefs = []
        if self.object and self.object.course_preferences:
            if isinstance(self.object.course_preferences, list):
                # Filter out invalid preferences - only keep properly formatted ones
                current_prefs = [
                    pref for pref in self.object.course_preferences 
                    if pref and isinstance(pref, str) and '_' in pref and len(pref) > 3
                ]
        
        context.update({
            'institutions': institutions,
            'courses_data_json': json.dumps(courses_data),
            'current_preferences': current_prefs
        })
        return context
    
    def dispatch(self, request, *args, **kwargs):
        # Check if student profile exists
        try:
            StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            messages.error(request, 'Please complete your profile first before applying.')
            return redirect('student:profile')
        return super().dispatch(request, *args, **kwargs)
    
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
            'form': DocumentUploadForm(student=student_profile),
        })
        return context
    
    def post(self, request, *args, **kwargs):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        form = DocumentUploadForm(request.POST, request.FILES, student=student_profile)
        
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
        messages.info(request, 'Document verification is now handled by administrators. Your documents will be reviewed shortly.')
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

class ChoiceSelectionView(StudentRequiredMixin, TemplateView):
    template_name = 'student/choice_selection.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allotment_id = kwargs.get('allotment_id')
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        allotment = get_object_or_404(SeatAllotment, id=allotment_id, student=student_profile)
        
        # Check if choice can still be made
        can_make_choice = allotment.student_choice == 'pending'
        
        context.update({
            'allotment': allotment,
            'can_make_choice': can_make_choice,
            'fee_amount': allotment.calculate_fee(),
        })
        return context
    
    def post(self, request, allotment_id):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        allotment = get_object_or_404(SeatAllotment, id=allotment_id, student=student_profile)
        
        choice = request.POST.get('choice')
        if choice and allotment.student_choice == 'pending':
            allotment.make_choice(choice)
            
            choice_messages = {
                'choice_1': f'You have accepted the seat for {allotment.allotted_course}. Please proceed with fee payment.',
                'choice_2': f'You have chosen to hold the seat and try for better options in the next round. Please proceed with fee payment.',
                'choice_3': f'You have rejected this seat and will participate in the next counseling round.',
                'choice_4': f'You have exited the counseling process. You will not participate in future rounds.',
            }
            
            messages.success(request, choice_messages.get(choice, 'Your choice has been recorded.'))
            
            # Redirect to payment if required
            if choice in ['choice_1', 'choice_2']:
                return redirect('student:payment', allotment_id=allotment.id)
        
        return redirect('student:allotment')

class PaymentView(StudentRequiredMixin, TemplateView):
    template_name = 'student/payment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allotment_id = kwargs.get('allotment_id')
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        allotment = get_object_or_404(SeatAllotment, id=allotment_id, student=student_profile)
        
        context.update({
            'allotment': allotment,
            'can_pay': allotment.payment_status == 'pending',
        })
        return context
    
    def post(self, request, allotment_id):
        student_profile = get_object_or_404(StudentProfile, user=request.user)
        allotment = get_object_or_404(SeatAllotment, id=allotment_id, student=student_profile)
        
        if allotment.payment_status == 'pending':
            # Process mock payment
            payment_success = allotment.process_mock_payment()
            
            if payment_success:
                if allotment.student_choice == 'choice_1':
                    messages.success(request, f'Payment successful! Your admission is confirmed. Admission Order: {allotment.admission_order_number}')
                else:
                    messages.success(request, f'Payment successful! Your seat is held for the next round. Reference: {allotment.payment_reference}')
            else:
                messages.error(request, 'Payment failed! Please try again.')
        
        return redirect('student:allotment')

class AdmissionOrderView(StudentRequiredMixin, TemplateView):
    template_name = 'student/admission_order.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allotment_id = kwargs.get('allotment_id')
        student_profile = get_object_or_404(StudentProfile, user=self.request.user)
        allotment = get_object_or_404(SeatAllotment, id=allotment_id, student=student_profile)
        
        # Only show admission order if payment is completed and choice was 1
        if allotment.admission_order_generated and allotment.payment_status == 'paid':
            context['allotment'] = allotment
        else:
            context['error'] = 'Admission order not available'
        
        return context


class AcceptSeatView(StudentRequiredMixin, TemplateView):
    def get(self, request, allotment_id):
        return redirect('student:choice_selection', allotment_id=allotment_id)
    
    def post(self, request, allotment_id):
        return redirect('student:choice_selection', allotment_id=allotment_id)