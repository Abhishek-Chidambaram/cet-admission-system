# admission/views.py
from django.shortcuts import render, redirect, get_object_or_404
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
    
    def handle_no_permission(self):
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(self.request, 'Access denied. Administrator login required.')
        return redirect('authentication:admin_login')

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
            'allotted_applications': Application.objects.filter(status='allotted').count(),
            'total_seat_allotments': SeatAllotment.objects.count(),
            'recent_applications': Application.objects.order_by('-created_at')[:10],
            'recent_allotments': SeatAllotment.objects.select_related('student__user', 'allotted_institution', 'counseling_round').order_by('-created_at')[:10],
            'counseling_rounds': CounselingRound.objects.all().order_by('round_number'),
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
                category_rank=MockDataGenerator.generate_rank_from_score(scores_data['total_score'], student.category) if student.category != 'GENERAL' else None,
            )
            generated_count += 1
        
        messages.success(request, f'Generated CET scores for {generated_count} students.')
        return redirect('admission:admin_dashboard')

class RunCounselingView(AdminRequiredMixin, TemplateView):
    template_name = 'admission/run_counseling.html'
    
    def prepare_students_for_counseling(self):
        """Ensure all students have applications and course preferences"""
        # Get available courses for preferences
        courses = Course.objects.filter(is_active=True)[:10]  # Get first 10 courses
        course_preferences = [f"{course.institution.code}_{course.course_code}" for course in courses]
        
        # Ensure all students have applications
        for student in StudentProfile.objects.all():
            # Create application if it doesn't exist
            application, created = Application.objects.get_or_create(student=student)
            
            # Add course preferences if empty
            if not application.course_preferences:
                # Give each student 3-5 random course preferences
                num_prefs = random.randint(3, min(5, len(course_preferences)))
                application.course_preferences = random.sample(course_preferences, num_prefs)
                application.save()
            
            # Auto-verify applications for counseling
            if application.status in ['draft', 'submitted']:
                application.status = 'verified'
                application.save()
    
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
            
            # Prepare all students for counseling
            self.prepare_students_for_counseling()
            
            # Get eligible students - more flexible criteria
            eligible_students = StudentProfile.objects.filter(
                cet_score__isnull=False
            ).order_by('cet_score__overall_rank')  # All students with CET scores
            
            institutions = Institution.objects.filter(is_active=True)
            courses = Course.objects.filter(is_active=True)
            
            allotted_count = 0
            for student in eligible_students:
                if not SeatAllotment.objects.filter(student=student).exists():
                    # Try to allot based on student's course preferences
                    allotted = False
                    
                    # Ensure student has an application
                    if not hasattr(student, 'application') or not student.application:
                        continue
                    
                    for preference in student.application.course_preferences:
                        try:
                            course = None
                            
                            # Handle different preference formats
                            if '_' in preference:
                                # Format: "INSTITUTION_CODE_COURSE_CODE"
                                parts = preference.split('_')
                                if len(parts) >= 2:
                                    institution_code = parts[0]
                                    course_code = '_'.join(parts[1:])
                                    try:
                                        course = Course.objects.get(
                                            institution__code=institution_code,
                                            course_code=course_code,
                                            is_active=True
                                        )
                                    except Course.DoesNotExist:
                                        continue
                            else:
                                # Format: "CSE", "ISE", etc. - find any course with this code
                                course = Course.objects.filter(
                                    course_code=preference,
                                    is_active=True
                                ).first()
                            
                            if course:
                                # Check if seats are available (simplified logic)
                                existing_allotments = SeatAllotment.objects.filter(
                                    allotted_institution=course.institution,
                                    allotted_course=course.course_name,
                                    counseling_round=first_round
                                ).count()
                                
                                if existing_allotments < course.total_seats:
                                    # Handle None category
                                    student_category = student.category or 'GENERAL'
                                    
                                    SeatAllotment.objects.create(
                                        student=student,
                                        counseling_round=first_round,
                                        allotted_course=course.course_name,
                                        allotted_institution=course.institution,
                                        allotment_category=student_category,
                                    )
                                    
                                    # Update application status
                                    student.application.status = 'allotted'
                                    student.application.save()
                                    
                                    allotted_count += 1
                                    allotted = True
                                    break
                        except (ValueError, IndexError, AttributeError):
                            continue
                    
                    # If no preference could be satisfied, allot randomly as fallback
                    if not allotted and courses:
                        course = random.choice(list(courses))
                        # Handle None category
                        student_category = student.category or 'GENERAL'
                        
                        SeatAllotment.objects.create(
                            student=student,
                            counseling_round=first_round,
                            allotted_course=course.course_name,
                            allotted_institution=course.institution,
                            allotment_category=student_category,
                        )
                        
                        student.application.status = 'allotted'
                        student.application.save()
                        allotted_count += 1
            
            messages.success(request, f'Completed counseling round 1. Allotted seats to {allotted_count} students.')
        
        return redirect('admission:admin_dashboard')

class RunSpecificRoundView(AdminRequiredMixin, TemplateView):
    def post(self, request, round_number):
        """Run a specific counseling round"""
        from django.db import models
        
        # Create counseling rounds if they don't exist
        if not CounselingRound.objects.exists():
            rounds_data = MockDataGenerator.generate_mock_counseling_data()
            for round_data in rounds_data:
                CounselingRound.objects.create(**round_data)
        
        # Get or create the specific round
        counseling_round = CounselingRound.objects.filter(round_number=round_number).first()
        if not counseling_round:
            counseling_round = CounselingRound.objects.create(
                round_number=round_number,
                round_name=f"Counseling Round {round_number}",
                start_date=timezone.now(),
                end_date=timezone.now() + timezone.timedelta(days=7),
                is_active=True
            )
        else:
            counseling_round.is_active = True
            counseling_round.save()
        
        # Prepare students for counseling
        self.prepare_students_for_counseling()
        
        # Get eligible students based on round number
        if round_number == 1:
            # Round 1: All students with CET scores who don't have any allotments
            eligible_students = StudentProfile.objects.filter(
                cet_score__isnull=False
            ).exclude(
                allotments__isnull=False
            ).order_by('cet_score__overall_rank')
        else:
            # Round 2 and 3: All students with CET scores (they can get multiple allotments)
            eligible_students = StudentProfile.objects.filter(
                cet_score__isnull=False
            ).order_by('cet_score__overall_rank')
        
        courses = Course.objects.filter(is_active=True)
        allotted_count = 0
        
        for student in eligible_students:
            # For Round 1: Skip if student already has any allotment
            # For Round 2+: Skip only if student has an accepted allotment
            if round_number == 1:
                if SeatAllotment.objects.filter(student=student).exists():
                    continue
            else:
                if SeatAllotment.objects.filter(student=student, acceptance_status='accepted').exists():
                    continue
                
            # Try to allot based on student's course preferences
            allotted = False
            
            # Ensure student has an application
            if not hasattr(student, 'application') or not student.application:
                continue
            
            for preference in student.application.course_preferences:
                try:
                    course = None
                    
                    # Handle different preference formats
                    if '_' in preference:
                        # Format: "INSTITUTION_CODE_COURSE_CODE"
                        parts = preference.split('_')
                        if len(parts) >= 2:
                            institution_code = parts[0]
                            course_code = '_'.join(parts[1:])
                            try:
                                course = Course.objects.get(
                                    institution__code=institution_code,
                                    course_code=course_code,
                                    is_active=True
                                )
                            except Course.DoesNotExist:
                                continue
                    else:
                        # Format: "CSE", "ISE", etc. - find any course with this code
                        course = Course.objects.filter(
                            course_code=preference,
                            is_active=True
                        ).first()
                    
                    if course:
                        # Check if seats are available (count only accepted allotments)
                        existing_allotments = SeatAllotment.objects.filter(
                            allotted_institution=course.institution,
                            allotted_course=course.course_name,
                            acceptance_status='accepted'
                        ).count()
                        
                        if existing_allotments < course.total_seats:
                            # Handle None category
                            student_category = student.category or 'GENERAL'
                            
                            SeatAllotment.objects.create(
                                student=student,
                                counseling_round=counseling_round,
                                allotted_course=course.course_name,
                                allotted_institution=course.institution,
                                allotment_category=student_category,
                            )
                            
                            # Update application status
                            student.application.status = 'allotted'
                            student.application.save()
                            
                            allotted_count += 1
                            allotted = True
                            break
                except (ValueError, IndexError, AttributeError):
                    continue
            
            # If no preference could be satisfied, allot randomly as fallback
            if not allotted and courses:
                course = random.choice(list(courses))
                # Handle None category
                student_category = student.category or 'GENERAL'
                
                SeatAllotment.objects.create(
                    student=student,
                    counseling_round=counseling_round,
                    allotted_course=course.course_name,
                    allotted_institution=course.institution,
                    allotment_category=student_category,
                )
                
                student.application.status = 'allotted'
                student.application.save()
                allotted_count += 1
        
        messages.success(request, f'Completed counseling round {round_number}. Allotted seats to {allotted_count} students.')
        return redirect('admission:admin_dashboard')
    
    def prepare_students_for_counseling(self):
        """Ensure all students have applications and course preferences"""
        # Get available courses for preferences
        courses = Course.objects.filter(is_active=True)[:10]  # Get first 10 courses
        course_preferences = [f"{course.institution.code}_{course.course_code}" for course in courses]
        
        # Ensure all students have applications
        for student in StudentProfile.objects.all():
            # Create application if it doesn't exist
            application, _ = Application.objects.get_or_create(student=student)
            
            # Add course preferences if empty
            if not application.course_preferences:
                # Give each student 3-5 random course preferences
                num_prefs = random.randint(3, min(5, len(course_preferences)))
                application.course_preferences = random.sample(course_preferences, num_prefs)
                application.save()
            
            # Auto-verify applications for counseling
            if application.status in ['draft', 'submitted']:
                application.status = 'verified'
                application.save()

class UndoCounselingView(AdminRequiredMixin, TemplateView):
    template_name = 'admission/undo_counseling.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        round_id = kwargs.get('round_id')
        if round_id:
            counseling_round = get_object_or_404(CounselingRound, id=round_id)
            allotments = SeatAllotment.objects.filter(counseling_round=counseling_round)
            context.update({
                'counseling_round': counseling_round,
                'allotments': allotments,
                'allotments_count': allotments.count(),
            })
        return context
    
    def post(self, request, round_id):
        counseling_round = get_object_or_404(CounselingRound, id=round_id)
        
        # Get all allotments for this round
        allotments = SeatAllotment.objects.filter(counseling_round=counseling_round)
        allotments_count = allotments.count()
        
        # Reset application status for affected students
        for allotment in allotments:
            if allotment.student.application:
                allotment.student.application.status = 'verified'
                allotment.student.application.save()
        
        # Delete all allotments for this round
        allotments.delete()
        
        # Deactivate the counseling round
        counseling_round.is_active = False
        counseling_round.save()
        
        messages.success(request, f'Successfully undone counseling round {counseling_round.round_number}. Removed {allotments_count} seat allotments.')
        return redirect('admission:admin_dashboard')

class SeatAllotmentListView(AdminRequiredMixin, ListView):
    model = SeatAllotment
    template_name = 'admission/seat_allotments.html'
    context_object_name = 'allotments'
    paginate_by = 50
    
    def get_queryset(self):
        return SeatAllotment.objects.select_related(
            'student__user', 'allotted_institution', 'counseling_round'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_allotments': SeatAllotment.objects.count(),
            'accepted_allotments': SeatAllotment.objects.filter(acceptance_status='accepted').count(),
            'pending_allotments': SeatAllotment.objects.filter(acceptance_status='pending').count(),
        })
        return context

class DocumentVerificationView(AdminRequiredMixin, TemplateView):
    template_name = 'admission/document_verification.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from student.models import StudentDocument
        
        context.update({
            'pending_documents': StudentDocument.objects.filter(verification_status='pending').select_related('student__user'),
            'verified_documents': StudentDocument.objects.filter(verification_status='verified').select_related('student__user')[:20],
            'rejected_documents': StudentDocument.objects.filter(verification_status='rejected').select_related('student__user')[:20],
        })
        return context

class VerifyDocumentAdminView(AdminRequiredMixin, TemplateView):
    def post(self, request, doc_id):
        from student.models import StudentDocument
        document = get_object_or_404(StudentDocument, id=doc_id)
        action = request.POST.get('action')
        
        if action == 'verify':
            document.verification_status = 'verified'
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.save()
            messages.success(request, f'Document {document.document_type} for {document.student.user.username} has been verified.')
        
        elif action == 'reject':
            document.verification_status = 'rejected'
            document.verified_by = request.user
            document.verified_at = timezone.now()
            document.rejection_reason = request.POST.get('rejection_reason', 'Document does not meet requirements')
            document.save()
            messages.warning(request, f'Document {document.document_type} for {document.student.user.username} has been rejected.')
        
        return redirect('admission:document_verification')

class ResultsView(TemplateView):
    template_name = 'admission/results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'top_rankers': CETScore.objects.order_by('overall_rank')[:10],
            'total_students': CETScore.objects.count(),
        })
        return context