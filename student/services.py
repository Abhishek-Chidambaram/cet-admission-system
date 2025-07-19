# student/services.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
import io
import logging
from PIL import Image as PILImage
import os

from .models import StudentProfile, Application, StudentDocument, StudentNotification, HallTicket, CETScore
from authentication.models import User

logger = logging.getLogger(__name__)

class StudentService:
    """Service class for student operations"""
    
    @staticmethod
    def create_student_profile(user, profile_data):
        """Create student profile with initial data"""
        try:
            profile = StudentProfile.objects.create(
                user=user,
                **profile_data
            )
            
            # Calculate initial profile completion
            profile.calculate_profile_completion()
            profile.save()
            
            # Create welcome notification
            StudentService.create_notification(
                student=profile,
                title="Welcome to CET Admission System!",
                message="Your account has been created successfully. Please complete your profile to continue.",
                notification_type='info',
                action_url='/student/profile/',
                action_text='Complete Profile'
            )
            
            return profile, None
            
        except Exception as e:
            logger.error(f"Error creating student profile: {str(e)}")
            return None, "Error creating student profile"
    
    @staticmethod
    def update_student_profile(profile, profile_data):
        """Update student profile"""
        try:
            for field, value in profile_data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            profile.calculate_profile_completion()
            profile.save()
            
            # Create notification if profile is complete
            if profile.is_profile_complete:
                StudentService.create_notification(
                    student=profile,
                    title="Profile Completed!",
                    message="Your profile is now complete. You can proceed with your application.",
                    notification_type='success',
                    action_url='/student/application/',
                    action_text='Start Application'
                )
            
            return profile, None
            
        except Exception as e:
            logger.error(f"Error updating student profile: {str(e)}")
            return None, "Error updating profile"
    
    @staticmethod
    def create_application(student, application_data):
        """Create new application"""
        try:
            application = Application.objects.create(
                student=student,
                **application_data
            )
            
            # Create notification
            StudentService.create_notification(
                student=student,
                title="Application Created",
                message=f"Application {application.application_number} has been created successfully.",
                notification_type='success',
                action_url=f'/student/application/{application.id}/',
                action_text='View Application'
            )
            
            return application, None
            
        except Exception as e:
            logger.error(f"Error creating application: {str(e)}")
            return None, "Error creating application"
    
    @staticmethod
    def submit_application(application):
        """Submit application for review"""
        try:
            if not application.can_edit():
                return False, "Application cannot be submitted in current status"
            
            # Check if profile is complete
            if not application.student.is_profile_complete:
                return False, "Please complete your profile before submitting application"
            
            # Check required documents
            required_documents = ['photo', 'signature', '12th_certificate', 'cet_score_card']
            uploaded_documents = application.student.documents.filter(
                document_type__in=required_documents
            ).count()
            
            if uploaded_documents < len(required_documents):
                return False, "Please upload all required documents before submitting"
            
            # Submit application
            success = application.submit_application()
            
            if success:
                # Create notification
                StudentService.create_notification(
                    student=application.student,
                    title="Application Submitted",
                    message=f"Application {application.application_number} has been submitted successfully.",
                    notification_type='success',
                    action_url=f'/student/application/{application.id}/',
                    action_text='View Application'
                )
                
                # Send email notification
                StudentService.send_application_submitted_email(application)
            
            return success, None
            
        except Exception as e:
            logger.error(f"Error submitting application: {str(e)}")
            return False, "Error submitting application"
    
    @staticmethod
    def upload_document(student, document_type, document_file, document_name):
        """Upload student document"""
        try:
            # Check file size (5MB limit)
            if document_file.size > 5 * 1024 * 1024:
                return None, "File size should not exceed 5MB"
            
            # Check file type
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            file_extension = '.' + document_file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                return None, "File type not allowed"
            
            # Delete existing document of same type
            StudentDocument.objects.filter(
                student=student,
                document_type=document_type
            ).delete()
            
            # Create new document
            document = StudentDocument.objects.create(
                student=student,
                document_type=document_type,
                document_name=document_name,
                document_file=document_file
            )
            
            # Create notification
            StudentService.create_notification(
                student=student,
                title="Document Uploaded",
                message=f"Document '{document_name}' has been uploaded successfully.",
                notification_type='success',
                action_url='/student/documents/',
                action_text='View Documents'
            )
            
            return document, None
            
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return None, "Error uploading document"
    
    @staticmethod
    def generate_hall_ticket(student):
        """Generate hall ticket for student"""
        try:
            # Check if student has CET score
            if not hasattr(student, 'cet_score'):
                return None, "CET score not found"
            
            # Create or get hall ticket
            hall_ticket, created = HallTicket.objects.get_or_create(
                student=student,
                defaults={
                    'exam_date': timezone.now().date(),
                    'exam_time': timezone.now().time(),
                    'exam_center': 'CET Examination Center',
                    'exam_center_address': 'Main Campus, City',
                    'instructions': StudentService.get_hall_ticket_instructions()
                }
            )
            
            if not hall_ticket.is_generated:
                # Generate PDF
                pdf_buffer = StudentService.create_hall_ticket_pdf(hall_ticket)
                
                # Save PDF file
                pdf_file = ContentFile(pdf_buffer.getvalue())
                hall_ticket.hall_ticket_file.save(
                    f'hall_ticket_{hall_ticket.ticket_number}.pdf',
                    pdf_file,
                    save=False
                )
                
                hall_ticket.is_generated = True
                hall_ticket.generated_at = timezone.now()
                hall_ticket.save()
                
                # Create notification
                StudentService.create_notification(
                    student=student,
                    title="Hall Ticket Generated",
                    message="Your hall ticket has been generated successfully.",
                    notification_type='success',
                    action_url='/student/hall-ticket/',
                    action_text='Download Hall Ticket'
                )
            
            return hall_ticket, None
            
        except Exception as e:
            logger.error(f"Error generating hall ticket: {str(e)}")
            return None, "Error generating hall ticket"
    
    @staticmethod
    def create_hall_ticket_pdf(hall_ticket):
        """Create hall ticket PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Title
        title = Paragraph("CET ADMISSION SYSTEM", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Hall Ticket Header
        header = Paragraph("HALL TICKET", heading_style)
        story.append(header)
        story.append(Spacer(1, 12))
        
        # Student Information Table
        student_data = [
            ['Hall Ticket Number:', hall_ticket.ticket_number],
            ['Student ID:', hall_ticket.student.student_id],
            ['Student Name:', hall_ticket.student.user.get_full_name()],
            ['Date of Birth:', hall_ticket.student.date_of_birth.strftime('%d-%m-%Y')],
            ['Category:', hall_ticket.student.get_category_display()],
        ]
        
        if hasattr(hall_ticket.student, 'cet_score'):
            student_data.extend([
                ['CET Roll Number:', hall_ticket.student.cet_score.cet_roll_number],
                ['CET Score:', hall_ticket.student.cet_score.total_score],
                ['Rank:', hall_ticket.student.cet_score.overall_rank],
            ])
        
        student_table = Table(student_data, colWidths=[2*inch, 3*inch])
        student_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ]))
        
        story.append(student_table)
        story.append(Spacer(1, 20))
        
        # Exam Details
        exam_header = Paragraph("EXAMINATION DETAILS", heading_style)
        story.append(exam_header)
        story.append(Spacer(1, 12))
        
        exam_data = [
            ['Exam Name:', hall_ticket.exam_name],
            ['Exam Date:', hall_ticket.exam_date.strftime('%d-%m-%Y')],
            ['Exam Time:', hall_ticket.exam_time.strftime('%I:%M %p')],
            ['Exam Center:', hall_ticket.exam_center],
            ['Center Address:', hall_ticket.exam_center_address],
        ]
        
        exam_table = Table(exam_data, colWidths=[2*inch, 3*inch])
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 0), (0, -1), colors.blue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ]))
        
        story.append(exam_table)
        story.append(Spacer(1, 20))
        
        # Instructions
        instructions_header = Paragraph("INSTRUCTIONS", heading_style)
        story.append(instructions_header)
        story.append(Spacer(1, 12))
        
        instructions = Paragraph(hall_ticket.instructions, normal_style)
        story.append(instructions)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    @staticmethod
    def get_hall_ticket_instructions():
        """Get hall ticket instructions"""
        return """
        1. Report at the examination center 30 minutes before the examination time.
        2. Bring this hall ticket along with a valid photo ID proof.
        3. Mobile phones and electronic devices are not allowed in the examination hall.
        4. Use only blue or black ball point pen for marking answers.
        5. Do not write anything on the hall ticket except in the specified spaces.
        6. Follow all COVID-19 safety protocols as announced by the authorities.
        7. Any malpractice will result in immediate cancellation of candidature.
        8. The decision of the examination authorities shall be final and binding.
        """
    
    @staticmethod
    def create_notification(student, title, message, notification_type='info', action_url=None, action_text=None):
        """Create notification for student"""
        try:
            notification = StudentNotification.objects.create(
                student=student,
                title=title,
                message=message,
                notification_type=notification_type,
                action_url=action_url,
                action_text=action_text
            )
            
            # Send email notification if enabled
            if student.user.profile.notification_preferences.get('email_notifications', True):
                StudentService.send_notification_email(student, notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            return None
    
    @staticmethod
    def send_notification_email(student, notification):
        """Send notification email to student"""
        try:
            subject = f"CET Admission System - {notification.title}"
            
            context = {
                'student': student,
                'notification': notification
            }
            
            html_message = render_to_string('student/emails/notification_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Notification email sent to {student.user.email}")
            
        except Exception as e:
            logger.error(f"Error sending notification email: {str(e)}")
    
    @staticmethod
    def send_application_submitted_email(application):
        """Send application submitted email"""
        try:
            subject = f"Application Submitted - {application.application_number}"
            
            context = {
                'application': application,
                'student': application.student
            }
            
            html_message = render_to_string('student/emails/application_submitted_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[application.student.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Application submitted email sent to {application.student.user.email}")
            
        except Exception as e:
            logger.error(f"Error sending application submitted email: {str(e)}")
    
    @staticmethod
    def get_dashboard_data(student):
        """Get dashboard data for student"""
        try:
            # Get applications
            applications = Application.objects.filter(student=student).order_by('-created_at')
            
            # Get recent notifications
            notifications = StudentNotification.objects.filter(
                student=student,
                is_read=False
            ).order_by('-created_at')[:5]
            
            # Get document status
            document_counts = {
                'total': student.documents.count(),
                'verified': student.documents.filter(verification_status='verified').count(),
                'pending': student.documents.filter(verification_status='pending').count(),
                'rejected': student.documents.filter(verification_status='rejected').count(),
            }
            
            # Get profile completion
            profile_completion = student.profile_completion_percentage
            
            # Get hall ticket status
            hall_ticket_status = hasattr(student, 'hall_ticket') and student.hall_ticket.is_generated
            
            dashboard_data = {
                'student': student,
                'applications': applications,
                'notifications': notifications,
                'document_counts': document_counts,
                'profile_completion': profile_completion,
                'hall_ticket_status': hall_ticket_status,
                'has_cet_score': hasattr(student, 'cet_score'),
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {}
    
    @staticmethod
    def validate_document_upload(document_file, document_type):
        """Validate document upload"""
        errors = []
        
        # Check file size
        if document_file.size > 5 * 1024 * 1024:  # 5MB
            errors.append("File size should not exceed 5MB")
        
        # Check file type
        allowed_extensions = {
            'photo': ['.jpg', '.jpeg', '.png'],
            'signature': ['.jpg', '.jpeg', '.png'],
            'pdf_documents': ['.pdf'],
            'certificates': ['.pdf', '.jpg', '.jpeg', '.png'],
        }
        
        file_extension = '.' + document_file.name.split('.')[-1].lower()
        
        if document_type in ['photo', 'signature']:
            if file_extension not in allowed_extensions['photo']:
                errors.append("Only JPG, JPEG, PNG files are allowed for photos")
        elif document_type.endswith('_certificate'):
            if file_extension not in allowed_extensions['certificates']:
                errors.append("Only PDF, JPG, JPEG, PNG files are allowed for certificates")
        
        # Validate image dimensions for photos
        if document_type == 'photo' and file_extension in ['.jpg', '.jpeg', '.png']:
            try:
                image = PILImage.open(document_file)
                width, height = image.size
                
                # Check aspect ratio for passport photo
                aspect_ratio = width / height
                if not (0.7 <= aspect_ratio <= 0.8):
                    errors.append("Photo should be in passport size format (3:4 ratio)")
                
            except Exception:
                errors.append("Invalid image file")
        
        return errors
