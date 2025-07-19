# institution/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Institution(models.Model):
    """Engineering institutions offering CET courses"""
    INSTITUTION_TYPE_CHOICES = [
        ('government', 'Government'),
        ('aided', 'Government Aided'),
        ('unaided', 'Private Unaided'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    institution_type = models.CharField(max_length=20, choices=INSTITUTION_TYPE_CHOICES)
    
    # Contact Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, default='Karnataka')
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=17)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    
    # Admin user for this institution
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='managed_institution')
    
    # Status
    is_active = models.BooleanField(default=True)
    established_year = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Course(models.Model):
    """Engineering courses offered by institutions"""
    COURSE_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ISE', 'Information Science Engineering'),
        ('ECE', 'Electronics and Communication Engineering'),
        ('EEE', 'Electrical and Electronics Engineering'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('BIOTECH', 'Biotechnology'),
        ('CHEM', 'Chemical Engineering'),
        ('AERO', 'Aeronautical Engineering'),
        ('AUTO', 'Automobile Engineering'),
    ]
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='courses')
    course_code = models.CharField(max_length=10, choices=COURSE_CHOICES)
    course_name = models.CharField(max_length=100)
    
    # Seat Information
    total_seats = models.IntegerField()
    general_seats = models.IntegerField()
    obc_seats = models.IntegerField()
    sc_seats = models.IntegerField()
    st_seats = models.IntegerField()
    ews_seats = models.IntegerField()
    
    # Course Details
    duration_years = models.IntegerField(default=4)
    fees_per_year = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['institution', 'course_code']
    
    def __str__(self):
        return f"{self.institution.code} - {self.course_name}"

class SeatMatrix(models.Model):
    """Seat matrix for counseling rounds"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='seat_matrix')
    counseling_round = models.ForeignKey('student.CounselingRound', on_delete=models.CASCADE)
    
    # Available seats for this round
    available_general = models.IntegerField(default=0)
    available_obc = models.IntegerField(default=0)
    available_sc = models.IntegerField(default=0)
    available_st = models.IntegerField(default=0)
    available_ews = models.IntegerField(default=0)
    
    # Cutoff ranks for this round
    cutoff_general = models.IntegerField(null=True, blank=True)
    cutoff_obc = models.IntegerField(null=True, blank=True)
    cutoff_sc = models.IntegerField(null=True, blank=True)
    cutoff_st = models.IntegerField(null=True, blank=True)
    cutoff_ews = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['course', 'counseling_round']
    
    def __str__(self):
        return f"{self.course} - Round {self.counseling_round.round_number}"