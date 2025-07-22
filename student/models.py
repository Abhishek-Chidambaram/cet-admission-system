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
    CHOICE_OPTIONS = [
        ('choice_1', 'Choice 1: Accept Seat (Final)'),
        ('choice_2', 'Choice 2: Hold Seat, Try for Better'),
        ('choice_3', 'Choice 3: Reject Seat, Try Next Round'),
        ('choice_4', 'Choice 4: Exit Counselling'),
        ('pending', 'Pending Decision'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('not_required', 'Not Required'),
        ('pending', 'Payment Pending'),
        ('paid', 'Payment Completed'),
        ('failed', 'Payment Failed'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='allotments')
    counseling_round = models.ForeignKey(CounselingRound, on_delete=models.CASCADE)
    
    allotted_course = models.CharField(max_length=100)
    allotted_institution = models.ForeignKey('institution.Institution', on_delete=models.CASCADE)
    allotment_category = models.CharField(max_length=20)
    
    # New KCET Choice System
    student_choice = models.CharField(max_length=20, choices=CHOICE_OPTIONS, default='pending')
    choice_made_at = models.DateTimeField(null=True, blank=True)
    
    # Fee Payment (Mock)
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='not_required')
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=50, null=True, blank=True)
    
    # Admission Order
    admission_order_generated = models.BooleanField(default=False)
    admission_order_number = models.CharField(max_length=50, null=True, blank=True)
    
    # Legacy fields for backward compatibility
    acceptance_status = models.CharField(max_length=20, default='pending')
    is_accepted = models.BooleanField(default=False)
    acceptance_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def make_choice(self, choice):
        """Handle student's choice selection"""
        self.student_choice = choice
        self.choice_made_at = timezone.now()
        
        if choice == 'choice_1':
            # Accept seat - requires fee payment
            self.acceptance_status = 'accepted'
            self.is_accepted = True
            self.acceptance_date = timezone.now()
            self.fee_amount = self.calculate_fee()
            self.payment_status = 'pending'
            
        elif choice == 'choice_2':
            # Hold seat - requires fee payment
            self.acceptance_status = 'held'
            self.fee_amount = self.calculate_fee()
            self.payment_status = 'pending'
            
        elif choice == 'choice_3':
            # Reject seat - no fee required
            self.acceptance_status = 'rejected'
            self.payment_status = 'not_required'
            
        elif choice == 'choice_4':
            # Exit counselling
            self.acceptance_status = 'exited'
            self.payment_status = 'not_required'
            self.student.application.status = 'exited'
            self.student.application.save()
        
        self.save()
    
    def calculate_fee(self):
        """Calculate mock fee based on institution type and category"""
        base_fee = 50000  # Base fee
        
        # Adjust based on institution type
        if self.allotted_institution.institution_type == 'government':
            base_fee = 25000
        elif self.allotted_institution.institution_type == 'private':
            base_fee = 75000
        
        # Category-based fee reduction
        if self.allotment_category in ['SC', 'ST']:
            base_fee *= 0.5  # 50% reduction
        elif self.allotment_category in ['OBC', 'EWS']:
            base_fee *= 0.7  # 30% reduction
        
        return base_fee
    
    def process_mock_payment(self):
        """Simulate payment processing"""
        import random
        import string
        
        # 95% success rate for mock payment
        if random.random() <= 0.95:
            self.payment_status = 'paid'
            self.payment_date = timezone.now()
            self.payment_reference = 'PAY' + ''.join(random.choices(string.digits, k=10))
            
            # Generate admission order for Choice 1
            if self.student_choice == 'choice_1':
                self.generate_admission_order()
            
            self.save()
            return True
        else:
            self.payment_status = 'failed'
            self.save()
            return False
    
    def generate_admission_order(self):
        """Generate mock admission order"""
        if not self.admission_order_generated:
            year = timezone.now().year
            count = SeatAllotment.objects.filter(
                admission_order_generated=True,
                created_at__year=year
            ).count() + 1
            
            self.admission_order_number = f"ADM{year}{count:06d}"
            self.admission_order_generated = True
            
            # Update student application status
            self.student.application.status = 'admitted'
            self.student.application.save()
            
            self.save()
    
    def is_eligible_for_next_round(self):
        """Check if student is eligible for next counseling round"""
        if self.student_choice in ['choice_2', 'choice_3']:
            return True
        elif self.student_choice == 'choice_1' and self.payment_status == 'paid':
            return False  # Already admitted
        elif self.student_choice == 'choice_4':
            return False  # Exited counselling
        return True
    
    def get_choice_display_with_status(self):
        """Get choice display with payment status"""
        choice_display = self.get_student_choice_display()
        if self.student_choice in ['choice_1', 'choice_2'] and self.payment_status == 'pending':
            choice_display += f" (Payment Pending: ₹{self.fee_amount:,.2f})"
        elif self.student_choice in ['choice_1', 'choice_2'] and self.payment_status == 'paid':
            choice_display += f" (Paid: ₹{self.fee_amount:,.2f})"
        return choice_display
    
    # Legacy methods for backward compatibility
    def accept_seat(self):
        self.make_choice('choice_1')
    
    def reject_seat(self):
        self.make_choice('choice_3')
    
    def __str__(self):
        return f"{self.student.student_id} - {self.allotted_course} at {self.allotted_institution.name} (Round {self.counseling_round.round_number})"