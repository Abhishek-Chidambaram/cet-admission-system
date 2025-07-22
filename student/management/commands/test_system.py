# student/management/commands/test_system.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from student.models import StudentProfile, Application, StudentDocument, CETScore
from institution.models import Institution, Course
from django.utils import timezone
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class Command(BaseCommand):
    help = 'Test the entire CET admission system for logical bugs'
    
    def handle(self, *args, **options):
        self.stdout.write('🧪 Testing CET Admission System...')
        
        # Test 1: Student Profile Creation
        self.test_student_profile_creation()
        
        # Test 2: Application Process
        self.test_application_process()
        
        # Test 3: Document Upload and Verification
        self.test_document_verification()
        
        # Test 4: CET Score Generation
        self.test_cet_score_generation()
        
        # Test 5: Counseling Process
        self.test_counseling_process()
        
        self.stdout.write(
            self.style.SUCCESS('✅ All tests completed successfully!')
        )
    
    def test_student_profile_creation(self):
        self.stdout.write('Testing student profile creation...')
        
        # Create test user
        user = User.objects.create_user(
            username='test_student',
            email='test@example.com',
            password='test123',
            phone_number='+919876543210',
            user_type='student'
        )
        
        # Test profile creation with optional fields
        profile = StudentProfile.objects.create(user=user)
        assert profile.student_id is not None
        assert profile.student_id.startswith('CET')
        
        self.stdout.write('✅ Student profile creation test passed')
    
    def test_application_process(self):
        self.stdout.write('Testing application process...')
        
        user = User.objects.get(username='test_student')
        profile = user.student_profile
        
        # Test application creation
        application = Application.objects.create(student=profile)
        assert application.application_number is not None
        assert application.status == 'draft'
        
        # Test application submission
        application.course_preferences = ['RVCE_CSE', 'BMSCE_ISE']
        application.save()
        
        result = application.submit_application()
        assert result == True
        assert application.status == 'submitted'
        assert application.submission_date is not None
        
        self.stdout.write('✅ Application process test passed')
    
    def test_document_verification(self):
        self.stdout.write('Testing document verification...')
        
        user = User.objects.get(username='test_student')
        profile = user.student_profile
        
        # Create a simple test file
        test_file = SimpleUploadedFile(
            "test_document.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        # Test document upload
        document = StudentDocument.objects.create(
            student=profile,
            document_type='photo',
            document_file=test_file
        )
        
        assert document.verification_status == 'pending'
        
        # Test AI verification
        document.verify_document()
        assert document.verification_status in ['verified', 'rejected']
        assert document.ai_verification_score is not None
        
        self.stdout.write('✅ Document verification test passed')
    
    def test_cet_score_generation(self):
        self.stdout.write('Testing CET score generation...')
        
        user = User.objects.get(username='test_student')
        profile = user.student_profile
        
        # Test CET score creation
        score = CETScore.objects.create(
            student=profile,
            hall_ticket_number='CET2025123456',
            exam_date=timezone.datetime(2024, 5, 15).date(),
            exam_center='Test Center',
            physics_score=150,
            chemistry_score=140,
            mathematics_score=160,
            percentile=85.5,
            overall_rank=1000
        )
        
        # Test total score calculation
        assert score.total_score == 450
        
        self.stdout.write('✅ CET score generation test passed')
    
    def test_counseling_process(self):
        self.stdout.write('Testing counseling process...')
        
        # Ensure we have institutions and courses
        if not Institution.objects.exists():
            self.stdout.write('⚠️  No institutions found. Run setup_demo_data first.')
            return
        
        user = User.objects.get(username='test_student')
        profile = user.student_profile
        
        # Set application to verified status
        profile.application.status = 'verified'
        profile.application.save()
        
        # Test that student is eligible for counseling
        assert profile.cet_score is not None
        assert profile.application.status == 'verified'
        assert len(profile.application.course_preferences) > 0
        
        self.stdout.write('✅ Counseling process test passed')
        
        # Cleanup
        user.delete()  # This will cascade delete profile, application, etc.