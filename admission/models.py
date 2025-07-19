# admission/models.py
from django.db import models
from django.utils import timezone
import random

class CETExam(models.Model):
    """CET Exam details and configuration"""
    exam_year = models.IntegerField(unique=True)
    exam_name = models.CharField(max_length=200, default='Karnataka Common Entrance Test')
    
    # Exam dates
    application_start_date = models.DateField()
    application_end_date = models.DateField()
    exam_date = models.DateField()
    result_date = models.DateField()
    
    # Exam configuration
    total_marks = models.IntegerField(default=540)  # 180 each for PCM
    exam_duration_minutes = models.IntegerField(default=180)  # 3 hours
    
    # Status
    is_active = models.BooleanField(default=True)
    is_result_published = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"CET {self.exam_year}"

class ExamCenter(models.Model):
    """CET Exam centers"""
    center_code = models.CharField(max_length=10, unique=True)
    center_name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    capacity = models.IntegerField()
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.center_code} - {self.center_name}"

class MockDataGenerator:
    """Utility class to generate mock data for CET system"""
    
    @staticmethod
    def generate_hall_ticket():
        """Generate random hall ticket number"""
        year = timezone.now().year
        return f"CET{year}{random.randint(100000, 999999)}"
    
    @staticmethod
    def generate_cet_scores():
        """Generate realistic CET scores"""
        # Generate scores with some correlation (good students tend to score well in all subjects)
        base_ability = random.uniform(0.3, 1.0)  # Student's overall ability
        
        physics = int(base_ability * 180 + random.uniform(-30, 30))
        chemistry = int(base_ability * 180 + random.uniform(-30, 30))
        mathematics = int(base_ability * 180 + random.uniform(-30, 30))
        
        # Ensure scores are within valid range
        physics = max(0, min(180, physics))
        chemistry = max(0, min(180, chemistry))
        mathematics = max(0, min(180, mathematics))
        
        total = physics + chemistry + mathematics
        percentile = min(99.99, max(0.01, base_ability * 100 + random.uniform(-10, 10)))
        
        return {
            'physics_score': physics,
            'chemistry_score': chemistry,
            'mathematics_score': mathematics,
            'total_score': total,
            'percentile': round(percentile, 2)
        }
    
    @staticmethod
    def generate_rank_from_score(total_score, category='GENERAL'):
        """Generate rank based on total score"""
        # Rough mapping of score to rank (higher score = better rank)
        max_score = 540
        score_percentage = total_score / max_score
        
        if category == 'GENERAL':
            # General category has more competition
            base_rank = int((1 - score_percentage) * 50000) + 1
        else:
            # Reserved categories have slightly better ranks for same score
            base_rank = int((1 - score_percentage) * 30000) + 1
        
        # Add some randomness
        rank_variation = random.randint(-500, 500)
        final_rank = max(1, base_rank + rank_variation)
        
        return final_rank
    
    @staticmethod
    def assign_exam_center():
        """Assign random exam center"""
        centers = [
            'Bangalore North', 'Bangalore South', 'Mysore', 'Mangalore',
            'Hubli', 'Belgaum', 'Gulbarga', 'Davangere', 'Shimoga', 'Udupi'
        ]
        return random.choice(centers)
    
    @staticmethod
    def generate_mock_counseling_data():
        """Generate mock counseling rounds"""
        current_year = timezone.now().year
        
        rounds = [
            {
                'round_number': 1,
                'round_name': 'First Round',
                'start_date': timezone.datetime(current_year, 8, 1),
                'end_date': timezone.datetime(current_year, 8, 7),
            },
            {
                'round_number': 2,
                'round_name': 'Second Round',
                'start_date': timezone.datetime(current_year, 8, 15),
                'end_date': timezone.datetime(current_year, 8, 21),
            },
            {
                'round_number': 3,
                'round_name': 'Mop-up Round',
                'start_date': timezone.datetime(current_year, 8, 25),
                'end_date': timezone.datetime(current_year, 8, 28),
            }
        ]
        
        return rounds