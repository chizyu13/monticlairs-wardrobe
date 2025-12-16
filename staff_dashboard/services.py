from django.utils import timezone
from django.contrib.auth.models import User
from staff_dashboard.models import StaffApproval, StaffAuditLog


class StaffApprovalService:
    """
    Service class for managing staff approval operations.
    """
    
    @staticmethod
    def approve_staff(user, approved_by):
        """
        Approve a staff member.
        
        Args:
            user: User instance to approve
            approved_by: User instance (admin) who is approving
            
        Returns:
            StaffApproval instance
        """
        approval, created = StaffApproval.objects.get_or_create(user=user)
        approval.is_approved = True
        approval.approved_by = approved_by
        approval.approved_at = timezone.now()
        approval.revoked_at = None  # Clear revoked timestamp if re-approving
        approval.save()
        return approval
    
    @staticmethod
    def revoke_staff(user):
        """
        Revoke staff approval.
        
        Args:
            user: User instance to revoke approval for
            
        Returns:
            StaffApproval instance
        """
        approval = StaffApproval.objects.get(user=user)
        approval.is_approved = False
        approval.revoked_at = timezone.now()
        approval.save()
        return approval
    
    @staticmethod
    def get_pending_staff():
        """
        Get all staff members pending approval.
        
        Returns:
            QuerySet of StaffApproval instances where is_approved=False
        """
        return StaffApproval.objects.filter(
            is_approved=False,
            user__is_staff=True,
            user__is_superuser=False
        ).select_related('user')
    
    @staticmethod
    def get_approved_staff():
        """
        Get all approved staff members.
        
        Returns:
            QuerySet of StaffApproval instances where is_approved=True
        """
        return StaffApproval.objects.filter(
            is_approved=True,
            user__is_staff=True,
            user__is_superuser=False
        ).select_related('user', 'approved_by')
    
    @staticmethod
    def get_all_staff():
        """
        Get all staff members with their approval status.
        
        Returns:
            QuerySet of StaffApproval instances for all staff users
        """
        return StaffApproval.objects.filter(
            user__is_staff=True,
            user__is_superuser=False
        ).select_related('user', 'approved_by')


class AuditLogService:
    """
    Service class for managing audit log operations.
    """
    
    @staticmethod
    def log_action(staff_member, action, target_model, target_id, changes):
        """
        Create an audit log entry.
        
        Args:
            staff_member: User instance who performed the action
            action: Action type (from StaffAuditLog.ACTION_CHOICES)
            target_model: Name of the model being modified
            target_id: ID of the target object
            changes: Dictionary of changes made
            
        Returns:
            StaffAuditLog instance
        """
        return StaffAuditLog.objects.create(
            staff_member=staff_member,
            action=action,
            target_model=target_model,
            target_id=target_id,
            changes=changes
        )
    
    @staticmethod
    def get_audit_log(staff_member=None, action=None, limit=None):
        """
        Get audit log entries with optional filtering.
        
        Args:
            staff_member: Optional User instance to filter by
            action: Optional action type to filter by
            limit: Optional limit on number of results
            
        Returns:
            QuerySet of StaffAuditLog instances
        """
        queryset = StaffAuditLog.objects.all().select_related('staff_member')
        
        if staff_member:
            queryset = queryset.filter(staff_member=staff_member)
        
        if action:
            queryset = queryset.filter(action=action)
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_staff_actions(staff_member, limit=None):
        """
        Get all actions performed by a specific staff member.
        
        Args:
            staff_member: User instance
            limit: Optional limit on number of results
            
        Returns:
            QuerySet of StaffAuditLog instances
        """
        queryset = StaffAuditLog.objects.filter(
            staff_member=staff_member
        ).select_related('staff_member')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_recent_logs(limit=50):
        """
        Get the most recent audit log entries.
        
        Args:
            limit: Number of entries to return (default 50)
            
        Returns:
            QuerySet of StaffAuditLog instances
        """
        return StaffAuditLog.objects.all().select_related('staff_member')[:limit]
