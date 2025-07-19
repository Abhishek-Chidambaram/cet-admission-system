# api/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from student.models import StudentProfile, Application
from institution.models import Institution
from .serializers import StudentSerializer, InstitutionSerializer, ApplicationSerializer
import random
import time

User = get_user_model()

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class InstitutionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsAuthenticated]

class ApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

class MockNotificationView(APIView):
    """Mock notification service - simulates SMS/Email notifications"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        notification_type = request.data.get('type', 'email')
        recipient = request.data.get('recipient')
        message = request.data.get('message', 'Test notification')
        
        # Simulate processing time
        time.sleep(1)
        
        # Mock success/failure
        success = random.choice([True, True, True, False])  # 75% success rate
        
        if success:
            return Response({
                'status': 'success',
                'message': f'Mock {notification_type} sent to {recipient}',
                'notification_id': f'MOCK_{random.randint(100000, 999999)}',
                'timestamp': time.time()
            })
        else:
            return Response({
                'status': 'failed',
                'message': f'Failed to send {notification_type} to {recipient}',
                'error': 'Mock service temporarily unavailable'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MockPaymentView(APIView):
    """Mock payment gateway - simulates payment processing"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        amount = request.data.get('amount', 0)
        payment_method = request.data.get('payment_method', 'card')
        
        # Simulate processing time
        time.sleep(2)
        
        # Mock success/failure
        success = random.choice([True, True, True, True, False])  # 80% success rate
        
        if success:
            return Response({
                'status': 'success',
                'transaction_id': f'TXN_{random.randint(1000000000, 9999999999)}',
                'amount': amount,
                'payment_method': payment_method,
                'gateway': 'MockPay',
                'timestamp': time.time(),
                'receipt_url': f'/mock-receipt/{random.randint(100000, 999999)}'
            })
        else:
            return Response({
                'status': 'failed',
                'error': 'Payment declined by mock bank',
                'error_code': f'ERR_{random.randint(1000, 9999)}'
            }, status=status.HTTP_400_BAD_REQUEST)