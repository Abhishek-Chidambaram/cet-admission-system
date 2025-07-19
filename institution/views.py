from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from .models import Institution, Course, SeatMatrix
from student.models import SeatAllotment, StudentProfile

class InstitutionRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.user_type == 'institution'

class InstitutionDashboardView(InstitutionRequiredMixin, TemplateView):
    template_name = 'institution/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            institution = self.request.user.managed_institution
            context.update({
                'institution': institution,
                'total_courses': institution.courses.count(),
                'total_seats': sum(course.total_seats for course in institution.courses.all()),
                'admitted_students': SeatAllotment.objects.filter(
                    allotted_institution=institution,
                    is_accepted=True
                ).count(),
                'recent_admissions': SeatAllotment.objects.filter(
                    allotted_institution=institution,
                    is_accepted=True
                ).order_by('-acceptance_date')[:10],
            })
        except Institution.DoesNotExist:
            context['no_institution'] = True
        return context

class CourseListView(InstitutionRequiredMixin, ListView):
    model = Course
    template_name = 'institution/courses.html'
    context_object_name = 'courses'
    
    def get_queryset(self):
        try:
            institution = self.request.user.managed_institution
            return institution.courses.all()
        except Institution.DoesNotExist:
            return Course.objects.none()

class AdmittedStudentsView(InstitutionRequiredMixin, ListView):
    model = SeatAllotment
    template_name = 'institution/students.html'
    context_object_name = 'allotments'
    paginate_by = 20
    
    def get_queryset(self):
        try:
            institution = self.request.user.managed_institution
            return SeatAllotment.objects.filter(
                allotted_institution=institution,
                is_accepted=True
            ).select_related('student__user', 'counseling_round')
        except Institution.DoesNotExist:
            return SeatAllotment.objects.none()

class SeatMatrixView(InstitutionRequiredMixin, TemplateView):
    template_name = 'institution/seat_matrix.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            institution = self.request.user.managed_institution
            courses = institution.courses.all()
            
            seat_data = []
            for course in courses:
                allotted_count = SeatAllotment.objects.filter(
                    allotted_institution=institution,
                    allotted_course=course.course_name,
                    is_accepted=True
                ).count()
                
                seat_data.append({
                    'course': course,
                    'allotted': allotted_count,
                    'remaining': course.total_seats - allotted_count
                })
            
            context.update({
                'institution': institution,
                'seat_data': seat_data,
            })
        except Institution.DoesNotExist:
            context['no_institution'] = True
        return context