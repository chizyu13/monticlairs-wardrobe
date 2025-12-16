from django.shortcuts import redirect, render
from django.urls import reverse
from staff_dashboard.models import StaffApproval


class StaffApprovalMiddleware:
    """
    Middleware to check staff approval status for staff dashboard access.
    
    This middleware ensures that:
    - Only authenticated users can access /staff/ URLs
    - Only users with is_staff=True can access /staff/ URLs
    - Staff members must be approved before accessing the dashboard
    - Superusers always have access (bypass approval check)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if the request is for a staff dashboard URL
        if request.path.startswith('/staff/'):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.path}")
            
            # Check if user has staff status
            if not request.user.is_staff:
                return redirect('home:main_page')
            
            # Superusers always have access
            if request.user.is_superuser:
                return self.get_response(request)
            
            # Check staff approval status
            try:
                approval = StaffApproval.objects.get(user=request.user)
                if not approval.is_approved:
                    return render(request, 'staff/pending_approval.html', {
                        'user': request.user
                    })
            except StaffApproval.DoesNotExist:
                # No approval record exists, show pending approval page
                return render(request, 'staff/pending_approval.html', {
                    'user': request.user
                })
        
        return self.get_response(request)
