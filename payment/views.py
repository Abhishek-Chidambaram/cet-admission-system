from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

def plans_view(request):
    """View function for displaying available payment plans."""
    # Define the available plans
    plans = [
        {
            'name': 'Basic',
            'price': 0,
            'features': [
                'Basic Counseling',
                'Document Upload',
                'Hall Ticket Download',
                'Basic Notifications',
                'Rank Viewing'
            ],
            'button_text': 'Current Plan',
            'button_class': 'btn-secondary',
            'disabled': True
        },
        {
            'name': 'Premium',
            'price': 999,
            'features': [
                'Premium Counseling',
                'AI Document Verification',
                'Mock Allotment',
                'Priority Support',
                'Detailed Analytics',
                'Advanced Notifications'
            ],
            'button_text': 'Upgrade Now',
            'button_class': 'btn-warning',
            'disabled': False
        }
    ]
    
    context = {
        'plans': plans,
        'title': 'Premium Plans',
    }
    
    return render(request, 'payment/plans.html', context)
