from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import LeaveRequest
from .services.email_service import LeaveEmailService
import logging
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)


# Store original status to detect changes
_leave_status_cache = {}

@login_required
@receiver(pre_save, sender=LeaveRequest)
def cache_leave_status(sender, instance, **kwargs):
    """Cache the original status before save"""
    try:
        original = LeaveRequest.objects.get(pk=instance.pk)
        _leave_status_cache[instance.pk] = {
            'status': original.status,
        }
    except LeaveRequest.DoesNotExist:
        # New leave being created
        _leave_status_cache[instance.pk] = {
            'status': None,
        }

@login_required
@receiver(post_save, sender=LeaveRequest)
def send_leave_emails(sender, instance, created, **kwargs):
    """Automatically send emails based on leave status changes"""
    
    try:
        if not instance.user:
            logger.error(f"LeaveRequest {instance.pk} has no associated user - email not sent")
            return  # Exit early if no user
        
        cached_data = _leave_status_cache.get(instance.pk, {})
        old_status = cached_data.get('status')
        
        # New leave request created
        if created:
            logger.info(f"New leave request created by {instance.user.email}")
            LeaveEmailService.send_leave_request_email(instance)
        
        # Leave status changed to approved
        elif old_status and old_status != 'approved' and instance.status == 'approved':
            logger.info(f"Leave request approved for {instance.user.email}")
            LeaveEmailService.send_leave_approval_email(instance)
        
        # Leave status changed to rejected
        elif old_status and old_status != 'rejected' and instance.status == 'rejected':
            logger.info(f"Leave request rejected for {instance.user.email}")
            LeaveEmailService.send_leave_rejection_email(instance)
        
        # Leave status changed (other changes)
        elif old_status and old_status != instance.status:
            logger.info(f"Leave status changed for {instance.user.email}: {old_status} → {instance.status}")
            LeaveEmailService.send_leave_status_email(instance, old_status, instance.status)
        
        # Clear cache
        if instance.pk in _leave_status_cache:
            del _leave_status_cache[instance.pk]
            
    except Exception as e:
        logger.error(f"Error in leave signal handler: {str(e)}")