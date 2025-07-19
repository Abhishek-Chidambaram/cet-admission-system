# student/management/commands/generate_cet_scores.py
from django.core.management.base import BaseCommand
from student.models import StudentProfile, CETScore
from admission.models import MockDataGenerator
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Generate CET scores for students who do not have them'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate scores for all students without scores',
        )
        parser.add_argument(
            '--student-id',
            type=str,
            help='Generate score for specific student ID',
        )
    
    def handle(self, *args, **options):
        if options['student_id']:
            # Generate for specific student
            try:
                student = StudentProfile.objects.get(student_id=options['student_id'])
                if hasattr(student, 'cet_score'):
                    self.stdout.write(
                        self.style.WARNING(f'Student {student.student_id} already has CET scores')
                    )
                    return
                
                self.generate_score_for_student(student)
                self.stdout.write(
                    self.style.SUCCESS(f'Generated CET score for student {student.student_id}')
                )
            except StudentProfile.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Student with ID {options["student_id"]} not found')
                )
        else:
            # Generate for all students without scores
            students_without_scores = StudentProfile.objects.filter(cet_score__isnull=True)
            
            if not students_without_scores.exists():
                self.stdout.write(
                    self.style.WARNING('All students already have CET scores')
                )
                return
            
            generated_count = 0
            for student in students_without_scores:
                self.generate_score_for_student(student)
                generated_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Generated CET scores for {generated_count} students')
            )
    
    def generate_score_for_student(self, student):
        """Generate CET score for a single student"""
        # Generate mock scores
        scores_data = MockDataGenerator.generate_cet_scores()
        rank = MockDataGenerator.generate_rank_from_score(scores_data['total_score'], student.category)
        
        # Generate category rank if not general category
        category_rank = None
        if student.category != 'GENERAL':
            category_rank = MockDataGenerator.generate_rank_from_score(scores_data['total_score'], student.category)
        
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
            category_rank=category_rank,
        )
        
        self.stdout.write(f'  - {student.student_id}: Score {scores_data["total_score"]}, Rank {rank}')