# student/management/commands/setup_demo_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from student.models import StudentProfile, CounselingRound
from institution.models import Institution, Course
from admission.models import CETExam, ExamCenter
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup demo data for CET admission system'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up demo data...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@cet.edu',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                phone_number='+919876543210',
                user_type='admin'
            )
            self.stdout.write(f'Created admin user: admin/admin123')
        
        # Create sample institutions
        institutions_data = [
            {
                'name': 'RV College of Engineering',
                'code': 'RVCE',
                'institution_type': 'private',
                'city': 'Bangalore',
                'established_year': 1963
            },
            {
                'name': 'BMS College of Engineering',
                'code': 'BMSCE',
                'institution_type': 'private',
                'city': 'Bangalore',
                'established_year': 1946
            },
            {
                'name': 'PES University',
                'code': 'PESU',
                'institution_type': 'private',
                'city': 'Bangalore',
                'established_year': 1972
            },
            {
                'name': 'Mysore University',
                'code': 'UOM',
                'institution_type': 'government',
                'city': 'Mysore',
                'established_year': 1916
            },
            {
                'name': 'NIE Institute of Technology',
                'code': 'NIET',
                'institution_type': 'government',
                'city': 'Mysore',
                'established_year': 1946
            }
        ]
        
        for inst_data in institutions_data:
            if not Institution.objects.filter(code=inst_data['code']).exists():
                # Create institution admin user
                admin_user = User.objects.create_user(
                    username=f"{inst_data['code'].lower()}_admin",
                    email=f"admin@{inst_data['code'].lower()}.edu",
                    password='admin123',
                    first_name=inst_data['name'],
                    last_name='Admin',
                    phone_number=f"+91987654{random.randint(1000, 9999)}",
                    user_type='institution'
                )
                
                institution = Institution.objects.create(
                    admin_user=admin_user,
                    address=f"{inst_data['name']} Campus, {inst_data['city']}",
                    pincode=f"{random.randint(560000, 580000)}",
                    phone=f"+91-80-{random.randint(20000000, 29999999)}",
                    email=f"info@{inst_data['code'].lower()}.edu",
                    **inst_data
                )
                
                # Create courses for each institution
                courses_data = [
                    ('CSE', 'Computer Science Engineering', 120, 50000),
                    ('ISE', 'Information Science Engineering', 60, 45000),
                    ('ECE', 'Electronics and Communication Engineering', 120, 40000),
                    ('MECH', 'Mechanical Engineering', 120, 35000),
                    ('CIVIL', 'Civil Engineering', 60, 30000),
                ]
                
                for course_code, course_name, total_seats, fees in courses_data:
                    Course.objects.create(
                        institution=institution,
                        course_code=course_code,
                        course_name=course_name,
                        total_seats=total_seats,
                        general_seats=int(total_seats * 0.5),
                        obc_seats=int(total_seats * 0.27),
                        sc_seats=int(total_seats * 0.15),
                        st_seats=int(total_seats * 0.075),
                        ews_seats=int(total_seats * 0.1),
                        fees_per_year=fees
                    )
                
                self.stdout.write(f'Created institution: {institution.name}')
        
        # Create CET Exam
        if not CETExam.objects.filter(exam_year=2024).exists():
            CETExam.objects.create(
                exam_year=2024,
                application_start_date=timezone.datetime(2024, 3, 1).date(),
                application_end_date=timezone.datetime(2024, 4, 30).date(),
                exam_date=timezone.datetime(2024, 5, 15).date(),
                result_date=timezone.datetime(2024, 6, 15).date(),
                is_result_published=True
            )
            self.stdout.write('Created CET Exam 2024')
        
        # Create exam centers
        centers_data = [
            ('BLR001', 'Bangalore North Center', 'Bangalore', 500),
            ('BLR002', 'Bangalore South Center', 'Bangalore', 500),
            ('MYS001', 'Mysore Center', 'Mysore', 300),
            ('HUB001', 'Hubli Center', 'Hubli', 200),
            ('MNG001', 'Mangalore Center', 'Mangalore', 200),
        ]
        
        for code, name, city, capacity in centers_data:
            if not ExamCenter.objects.filter(center_code=code).exists():
                ExamCenter.objects.create(
                    center_code=code,
                    center_name=name,
                    address=f"{name} Address, {city}",
                    city=city,
                    capacity=capacity
                )
        
        self.stdout.write('Created exam centers')
        
        # Create counseling rounds
        if not CounselingRound.objects.exists():
            rounds_data = [
                (1, 'First Round', timezone.make_aware(timezone.datetime(2024, 8, 1)), timezone.make_aware(timezone.datetime(2024, 8, 7))),
                (2, 'Second Round', timezone.make_aware(timezone.datetime(2024, 8, 15)), timezone.make_aware(timezone.datetime(2024, 8, 21))),
                (3, 'Mop-up Round', timezone.make_aware(timezone.datetime(2024, 8, 25)), timezone.make_aware(timezone.datetime(2024, 8, 28))),
            ]
            
            for round_num, round_name, start_date, end_date in rounds_data:
                CounselingRound.objects.create(
                    round_number=round_num,
                    round_name=round_name,
                    start_date=start_date,
                    end_date=end_date
                )
            
            self.stdout.write('Created counseling rounds')
        
        # Create sample student
        if not User.objects.filter(username='student1').exists():
            student_user = User.objects.create_user(
                username='student1',
                email='student1@example.com',
                password='student123',
                first_name='Rahul',
                last_name='Kumar',
                phone_number='+919876543211',
                user_type='student'
            )
            
            StudentProfile.objects.create(
                user=student_user,
                date_of_birth=timezone.datetime(2005, 6, 15).date(),
                gender='M',
                category='GENERAL',
                address='123 Main Street, Koramangala',
                city='Bangalore',
                state='Karnataka',
                pincode='560034',
                father_name='Suresh Kumar',
                mother_name='Priya Kumar',
                parent_phone='+919876543212',
                school_name='Delhi Public School',
                board='CBSE'
            )
            
            self.stdout.write('Created sample student: student1/student123')
        
        self.stdout.write(
            self.style.SUCCESS('Demo data setup completed successfully!')
        )
        self.stdout.write('Login credentials:')
        self.stdout.write('- Admin: admin/admin123')
        self.stdout.write('- Student: student1/student123')
        self.stdout.write('- Institution admins: {code}_admin/admin123 (e.g., rvce_admin/admin123)')