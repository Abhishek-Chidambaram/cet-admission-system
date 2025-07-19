# authentication/services.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import logging
import sys
from datetime import timedelta
from .models import User, OTPVerification, UserProfile, UserSession, LoginAttempt

logger = logging.getLogger(__name__)

class AuthenticationService:
    """Service class for authentication operations"""
    
    @staticmethod
    def create_user(email, phone_number, password, first_name, last_name, user_type='student'):
        """Create a new user with profile"""
        try:
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                return None, "Email already registered"
            
            if User.objects.filter(phone_number=phone_number).exists():
                return None, "Phone number already registered"
            
            # Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                notification_preferences={
                    'email_notifications': True,
                    'sms_notifications': True,
                    'push_notifications': True,
                    'marketing_emails': False
                }
            )
            
            return user, None
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None, "Error creating user account"
    
    @staticmethod
    def generate_and_send_otp(user, otp_type, contact_method='both'):
        """Generate and send OTP to user"""
        try:
            # Invalidate existing OTPs
            OTPVerification.objects.filter(
                user=user,
                otp_type=otp_type,
                is_verified=False
            ).update(is_verified=True)  # Mark as used
            
            # Generate new OTP
            otp_code = OTPVerification.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=5)
            
            # Create OTP record
            otp_record = OTPVerification.objects.create(
                user=user,
                otp_type=otp_type,
                otp_code=otp_code,
                email=user.email,
                phone_number=user.phone_number,
                expires_at=expires_at
            )
            
            # Send OTP via email
            if contact_method in ['email', 'both']:
                AuthenticationService.send_otp_email(user, otp_code, otp_type)
            
            # Send OTP via SMS
            if contact_method in ['sms', 'both']:
                AuthenticationService.send_otp_sms(user, otp_code, otp_type)
            
            return otp_record, None
            
        except Exception as e:
            logger.error(f"Error generating OTP: {str(e)}")
            return None, "Error sending OTP"
    
    @staticmethod
    def send_otp_email(user, otp_code, otp_type):
        """Mock OTP via console for development"""
        try:
            # In development, just print the OTP to console
            print(f"\n{'*' * 50}")
            print(f"DEBUG OTP for {user.email} ({otp_type}): {otp_code}")
            print(f"{'*' * 50}\n")
            
            # If you want to enable real email in production, uncomment below
            # subject = f"Your CET Admission System OTP - {otp_code}"
            
            context = {
                'user': user,
                'otp_code': otp_code,
                'otp_type': otp_type,
                'expiry_minutes': 5
            }
            
            html_message = render_to_string('authentication/emails/otp_email.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"OTP email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending OTP email: {str(e)}")
            return False
    
    @staticmethod
    def send_otp_sms(user, otp_code, otp_type):
        """Mock SMS OTP via console for development"""
        # In development, just print the SMS OTP to console
        print(f"\n{'*' * 50}")
        print(f"DEBUG SMS OTP for {user.phone_number} ({otp_type}): {otp_code}")
        print(f"{'*' * 50}\n")
        return True
    
    @staticmethod
    def verify_otp(user, otp_code, otp_type):
        """Verify OTP code"""
        try:
            otp_record = OTPVerification.objects.filter(
                user=user,
                otp_type=otp_type,
                otp_code=otp_code,
                is_verified=False
            ).first()
            
            if not otp_record:
                return False, "Invalid OTP code"
            
            if otp_record.is_expired():
                return False, "OTP has expired"
            
            if otp_record.attempts >= otp_record.max_attempts:
                return False, "Maximum attempts exceeded"
            
            # Increment attempts
            otp_record.attempts += 1
            otp_record.save()
            
            # Mark as verified
            otp_record.is_verified = True
            otp_record.save()
            
            # Update user verification status
            if otp_type == 'email_verification':
                user.is_email_verified = True
                user.save()
            elif otp_type == 'phone_verification':
                user.is_phone_verified = True
                user.save()
            
            return True, "OTP verified successfully"
            
        except Exception as e:
            logger.error(f"Error verifying OTP: {str(e)}")
            return False, "Error verifying OTP"
    
    @staticmethod
    def log_login_attempt(email, ip_address, user_agent, success, failure_reason=None):
        """Log login attempt for security"""
        try:
            LoginAttempt.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason
            )
        except Exception as e:
            logger.error(f"Error logging login attempt: {str(e)}")
    
    @staticmethod
    def create_user_session(user, request):
        """Create user session record"""
        try:
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # Get user agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create session record
            session = UserSession.objects.create(
                user=user,
                session_key=request.session.session_key,
                ip_address=ip_address,
                user_agent=user_agent,
                device_type=AuthenticationService.get_device_type(user_agent)
            )
            
            # Update user last login IP
            user.last_login_ip = ip_address
            user.save()
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating user session: {str(e)}")
            return None
    
    @staticmethod
    def get_device_type(user_agent):
        """Determine device type from user agent"""
        user_agent = user_agent.lower()
        
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        else:
            return 'desktop'
    
    @staticmethod
    def check_rate_limiting(ip_address, max_attempts=5, window_minutes=15):
        """Check if IP is rate limited"""
        try:
            since = timezone.now() - timedelta(minutes=window_minutes)
            attempts = LoginAttempt.objects.filter(
                ip_address=ip_address,
                success=False,
                created_at__gte=since
            ).count()
            
            return attempts >= max_attempts
            
        except Exception as e:
            logger.error(f"Error checking rate limiting: {str(e)}")
            return False
