from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import random

User = get_user_model()

class StudentProfile(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    CATEGORY_CHOICES = [
        ('GENERAL', 'General'),
        ('OBC', 'Other Backward Class'),
        ('SC', 'Scheduled Caste'),
        ('ST', 'Scheduled Tribe'),
        ('EWS', 'Economically Weaker Section'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=17)
    
    school_name = models.CharField(max_length=200)
    board = models.CharField(max_length=100)
    
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self.generate_student_id()
        super().save(*args, **kwargs)
    
    def generate_student_id(self):
        year = timezone.now().year
        count = StudentProfile.objects.filter(created_at__year=year).count() + 1
        return f"CET{year}{count:06d}"
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"

class CETScore(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='cet_score')
    
    hall_ticket_number = models.CharField(max_length=20, unique=True)
    exam_date = models.DateField()
    exam_center = models.CharField(max_length=200)
    
    physics_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(180)])
    chemistry_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(180)])
    mathematics_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(180)])
    
    total_score = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(540)])
    percentile = models.DecimalField(max_digits=5, decimal_places=2)
    
    overall_rank = models.IntegerField(validators=[MinValueValidator(1)])
    category_rank = models.IntegerField(validators=[MinValueValidator(1)], null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.total_score = self.physics_score + self.chemistry_score + self.mathematics_score
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.student_id} - Rank: {self.overall_rank}"

class Application(models.Model):
    APPLICATION_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('counseling', 'Counseling'),
        ('allotted', 'Seat Allotted'),
        ('admitted', 'Admitted'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='application')
    application_number = models.CharField(max_length=20, unique=True, editable=False)
    
    course_preferences = models.JSONField(default=list)
    
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='draft')
    submission_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = self.generate_application_number()
        super().save(*args, **kwargs)
    
    def generate_application_number(self):
        year = timezone.now().year
        count = Application.objects.filter(created_at__year=year).count() + 1
        return f"APP{year}{count:08d}"
    
    def submit_application(self):
        if self.status == 'draft':
            self.status = 'submitted'
            self.submission_date = timezone.now()
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.application_number} - {self.student.user.get_full_name()}"

class StudentDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('photo', 'Passport Size Photo'),
        ('10th_certificate', '10th Grade Certificate'),
        ('12th_certificate', '12th Grade Certificate'),
        ('cet_hall_ticket', 'CET Hall Ticket'),
        ('category_certificate', 'Category Certificate'),
        ('income_certificate', 'Income Certificate'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    document_file = models.FileField(upload_to='student_documents/')
    
    verification_status = models.CharField(max_length=30, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    ai_verification_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    verification_comments = models.TextField(blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def verify_document(self):
        """Mock AI verification - mostly successful with realistic scoring"""
        # Simulate AI verification with higher success rate (90% success)
        success_rate = random.random()
        
        if success_rate <= 0.9:  # 90% success rate
            self.ai_verification_score = round(random.uniform(85.0, 98.0), 2)
            self.verification_status = 'verified'
            self.verification_comments = f"Document verified successfully. AI confidence: {self.ai_verification_score}%. Document appears authentic and meets quality standards."
        else:  # 10% rejection rate
            self.ai_verification_score = round(random.uniform(60.0, 84.0), 2)
            self.verification_status = 'rejected'
            rejection_reasons = [
                "Document image quality is too low",
                "Text is not clearly visible",
                "Document appears to be incomplete",
                "Watermark or seal is not clear"
            ]
            reason = random.choice(rejection_reasons)
            self.verification_comments = f"Document verification failed. AI confidence: {self.ai_verification_score}%. Reason: {reason}. Please reupload a clearer image."
        
        self.save()
    
    def __str__(self):
        return f"{self.student.student_id} - {self.document_type}"

class CounselingRound(models.Model):
    round_number = models.IntegerField()
    round_name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Round {self.round_number} - {self.round_name}"

class SeatAllotment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='allotments')
    counseling_round = models.ForeignKey(CounselingRound, on_delete=models.CASCADE)
    
    allotted_course = models.CharField(max_length=100)
    allotted_institution = models.ForeignKey('institution.Institution', on_delete=models.CASCADE)
    allotment_category = models.CharField(max_length=20)
    
    is_accepted = models.BooleanField(default=False)
    acceptance_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def accept_seat(self):
        self.is_accepted = True
        self.acceptance_date = timezone.now()
        self.save()
        
        self.student.application.status = 'admitted'
        self.student.application.save()
    
    def __str__(self):
        return f"{self.student.student_id} - {self.allotted_course} at {self.allotted_institution.name}"