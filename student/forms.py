# student/forms.py
from django import forms
from .models import StudentProfile, Application, StudentDocument
from django.conf import settings

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            'date_of_birth', 'gender', 'category', 'address', 'city', 'state', 'pincode',
            'father_name', 'mother_name', 'parent_phone', 'school_name', 'board', 'photo'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class ApplicationForm(forms.ModelForm):
    course_preferences = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Select your preferred courses in order of preference (maximum 5)"
    )
    
    class Meta:
        model = Application
        fields = ['course_preferences']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get available courses from institutions
        from institution.models import Course
        course_choices = []
        
        courses = Course.objects.filter(is_active=True).select_related('institution').order_by('institution__name', 'course_name')
        for course in courses:
            choice_value = f"{course.institution.code}_{course.course_code}"
            choice_label = f"{course.course_name} - {course.institution.name} ({course.institution.code})"
            course_choices.append((choice_value, choice_label))
        
        self.fields['course_preferences'].choices = course_choices
        
        if self.instance and self.instance.course_preferences:
            self.fields['course_preferences'].initial = self.instance.course_preferences
    
    def clean_course_preferences(self):
        preferences = self.cleaned_data['course_preferences']
        if len(preferences) > 5:
            raise forms.ValidationError("You can select maximum 5 course preferences.")
        if len(preferences) == 0:
            raise forms.ValidationError("Please select at least one course preference.")
        return preferences

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ['document_type', 'document_file']
    
    def __init__(self, *args, **kwargs):
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
    
    def clean_document_type(self):
        document_type = self.cleaned_data['document_type']
        if self.student:
            # Check if this document type already exists for this student
            existing = StudentDocument.objects.filter(
                student=self.student,
                document_type=document_type
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                doc_type_display = dict(StudentDocument.DOCUMENT_TYPE_CHOICES).get(document_type, document_type)
                raise forms.ValidationError(f"You have already uploaded a {doc_type_display}. Please delete the existing one first.")
        
        return document_type