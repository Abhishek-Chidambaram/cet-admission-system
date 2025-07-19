# admission/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from student.models import StudentProfile, Application, CETScore, CounselingRound, SeatAllotment
from institution.models import Institution, Course
from .models import MockDataGenerator
import random

class HomeView(TemplateView):
    template_name = 'admission/home.html'

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'admin'

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'admission/admin_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_students': StudentProfile.objects.count(),
            'total_applications': Application.objects.count(),
            'total_institutions': Institution.objects.count(),
            'submitted_applications': Application.objects.filter(status='submitted').count(),
            'verified_applications': Application.objects.filter(status='verified').count(),
            'recent_applications': Application.objects.order_by('-created_at')[:10],
        })
        return context

class StudentListView(AdminRequiredMixin, ListView):
    model = StudentProfile
    template_name = 'admission/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

class InstitutionListView(AdminRequiredMixin, ListView):
    model = Institution
    template_name = 'admission/institution_list.html'
    context_object_name = 'institutions'
    paginate_by = 20

class CounselingManagementView(AdminRequiredMixin, TemplateView):
    template_name = 'admission/counseling_management.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'counseling_rounds': CounselingRound.objects.all().order_by('round_number'),
            'active_round': CounselingRound.objects.filter(is_active=True).first(),
        })
        return context

class GenerateScoresView(AdminRequiredMixin, TemplateView):
    template_name = 'admission/generate_scores.html'
    
    def post(self, request, *args, **kwargs):
        # Generate mock CET scores for students who don't have them
        students_without_scores = StudentProfile.objects.filter(cet_score__isnull=True)
        generated_count = 0
        
        for student in students_without_scores:
            # Generate mock scores
            scores_data = MockDataGenerator.generate_cet_scores()
            rank = MockDataGenerator.generate_rank_from_score(scores_data['total_score'], student.category)
            
            CETScore.objects.create(
                student=student,
                hall_ticket_number=MockDataGenerator.generate_hall_ticket(),
                exam_date=timezone.datetime(2024, 5, 15).date(),
                exam_center=MockDataGenerator.assign_exam_center(),
                physics_score=scores_data['physics_score'],
                chemistry_score=scores_data['chemistry_score'],
                mathematics_score=scores_data['mathematics_score'],
                total_score=scores_data['total_score'],
                percentile=scores_data['percentile'],
                overall_rank=rank,
                category_rank=rank if student.category != 'GENERAL' else None,
            )
            generated_count += 1
        
        messages.success(request, f'Generated CET scores for {generated_count} students.')
        return redirect('admission:admin_dashboard')

class RunCounselingView(AdminRequiredMixin, TemplateView):
    template_name = 'admission/run_counseling.html'
    
    def post(self, request, *args, **kwargs):
        # Create counseling rounds if they don't exist
        if not CounselingRound.objects.exists():
            rounds_data = MockDataGenerator.generate_mock_counseling_data()
            for round_data in rounds_data:
                CounselingRound.objects.create(**round_data)
        
        # Run mock seat allotment for first round
        first_round = CounselingRound.objects.filter(round_number=1).first()
        if first_round:
            first_round.is_active = True
            first_round.save()
            
            # Mock seat allotment logic
            eligible_students = StudentProfile.objects.filter(
                cet_score__isnull=False,
                application__status='verified'
            ).order_by('cet_score__overall_rank')[:100]  # Top 100 students
            
            institutions = Institution.objects.filter(is_active=True)
            courses = Course.objects.filter(is_active=True)
            
            allotted_count = 0
            for student in eligible_students:
                if not SeatAllotment.objects.filter(student=student).exists():
                    # Random course and institution for mock
                    course = random.choice(courses)
                    
                    SeatAllotment.objects.create(
                        student=student,
                        counseling_round=first_round,
                        allotted_course=course.course_name,
                        allotted_institution=course.institution,
                        allotment_category=student.category,
                    )
                    
                    # Update application status
                    student.application.status = 'allotted'
                    student.application.save()
                    
                    allotted_count += 1
            
            messages.success(request, f'Completed counseling round 1. Allotted seats to {allotted_count} students.')
        
        return redirect('admission:admin_dashboard')

class ResultsView(TemplateView):
    template_name = 'admission/results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'top_rankers': CETScore.objects.order_by('overall_rank')[:10],
            'total_students': CETScore.objects.count(),
        })
        return context