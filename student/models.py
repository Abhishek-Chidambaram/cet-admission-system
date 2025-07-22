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
    
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, null=True, blank=True)
    
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    
    father_name = models.CharField(max_length=100, null=True, blank=True)
    mother_name = models.CharField(max_length=100, null=True, blank=True)
    parent_phone = models.CharField(max_length=17, null=True, blank=True)
    
    school_name = models.CharField(max_length=200, null=True, blank=True)
    board = models.CharField(max_length=100, null=True, blank=True)
    
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
    
    def verify_application(self):
        """Verify application after document verification"""
        if self.status == 'submitted':
            # Check if all required documents are verified
            required_docs = ['photo', '10th_certificate', '12th_certificate']
            verified_docs = self.student.documents.filter(
                document_type__in=required_docs,
                verification_status='verified'
            ).count()
            
            if verified_docs >= len(required_docs):
                self.status = 'verified'
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
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_documents')
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)
    verification_comments = models.TextField(blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
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
    ACCEPTANCE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='allotments')
    counseling_round = models.ForeignKey(CounselingRound, on_delete=models.CASCADE)
    
    allotted_course = models.CharField(max_length=100)
    allotted_institution = models.ForeignKey('institution.Institution', on_delete=models.CASCADE)
    allotment_category = models.CharField(max_length=20)
    
    acceptance_status = models.CharField(max_length=20, choices=ACCEPTANCE_STATUS_CHOICES, default='pending')
    is_accepted = models.BooleanField(default=False)  # Keep for backward compatibility
    acceptance_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def accept_seat(self):
        self.acceptance_status = 'accepted'
        self.is_accepted = True
        self.acceptance_date = timezone.now()
        self.save()
        
        self.student.application.status = 'admitted'
        self.student.application.save()
    
    def reject_seat(self):
        self.acceptance_status = 'rejected'
        self.is_accepted = False
        self.acceptance_date = timezone.now()
        self.save()
    
    def __str__(self):
        return f"{self.student.student_id} - {self.allotted_course} at {self.allotted_institution.name}"