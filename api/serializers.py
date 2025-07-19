# api/serializers.py
from rest_framework import serializers
from student.models import StudentProfile, Application
from institution.models import Institution

class StudentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'student_id', 'user_name', 'user_email', 'date_of_birth',
            'gender', 'category', 'city', 'state', 'created_at'
        ]

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = [
            'id', 'name', 'code', 'institution_type', 'city', 'state',
            'established_year', 'is_active'
        ]

class ApplicationSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_id = serializers.CharField(source='student.student_id', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'application_number', 'student_name', 'student_id',
            'course_preferences', 'status', 'submission_date', 'created_at'
        ]