#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cet_admission_system.settings')
django.setup()

from student.models import StudentProfile, Application, CETScore, SeatAllotment
from institution.models import Course, Institution

print('=== DATABASE STATUS ===')
print(f'Total Students: {StudentProfile.objects.count()}')
print(f'Students with CET Scores: {StudentProfile.objects.filter(cet_score__isnull=False).count()}')
print(f'Total Applications: {Application.objects.count()}')
print(f'Applications with preferences: {Application.objects.exclude(course_preferences=[]).count()}')
print(f'Total Institutions: {Institution.objects.count()}')
print(f'Total Courses: {Course.objects.count()}')
print(f'Total Seat Allotments: {SeatAllotment.objects.count()}')

print('\n=== SAMPLE DATA ===')
# Check first few students
students = StudentProfile.objects.all()[:3]
for student in students:
    print(f'Student: {student.user.username}')
    print(f'  Has CET Score: {hasattr(student, "cet_score") and student.cet_score is not None}')
    print(f'  Has Application: {hasattr(student, "application") and student.application is not None}')
    if hasattr(student, 'application') and student.application:
        print(f'  Course Preferences: {student.application.course_preferences}')
        print(f'  Application Status: {student.application.status}')
    print()

# Check courses
courses = Course.objects.all()[:3]
print('Sample Courses:')
for course in courses:
    print(f'  {course.institution.code}_{course.course_code} - {course.course_name}')

# Check if there are any seat allotments
allotments = SeatAllotment.objects.all()[:5]
print(f'\nSample Seat Allotments ({len(allotments)}):')
for allotment in allotments:
    print(f'  {allotment.student.user.username} -> {allotment.allotted_course} at {allotment.allotted_institution.name}')