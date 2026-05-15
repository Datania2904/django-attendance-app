from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class LeaveEmailService:
    """Service for handling all leave request email notifications"""
    
    @staticmethod
    def get_manager_for_leave_type(leave_type):
        """Get manager details based on leave type"""
        managers = settings.LEAVE_MANAGERS
        # You can customize this logic based on leave type
        return managers.get('manager', managers.get('hr'))
    
    @staticmethod
    def send_leave_request_email(leave_request):
        """
        Send email when leave request is created
        Routes to appropriate manager
        """
        try:
            manager = LeaveEmailService.get_manager_for_leave_type(leave_request.leave_type)
            if not manager:
                logger.error(f"No manager found for leave type: {leave_request.leave_type}")
                return False
            
            user = leave_request.user
            manager_email = manager['email']
            
            # Prepare context for email template
            context = {
                'leave_request': leave_request,
                'employee_name': f"{user.first_name} {user.last_name}",
                'employee_email': user.email,
                'manager_name': manager['name'],
                'leave_type': leave_request.get_leave_type_display() if hasattr(leave_request, 'get_leave_type_display') else leave_request.leave_type,
                'start_date': leave_request.start_date,
                'end_date': leave_request.end_date,
                #'days': (leave_request.end_date - leave_request.start_date).days + 1,
                'reason': leave_request.reason,
                'leave_request_url': f"{settings.SITE_URL}/leaves/{leave_request.id}/"
            }
            
            # Render email template
            html_message = render_to_string('emails/leave_request.html', context)
            plain_message = strip_tags(html_message)
            
            # Create and send email
            email = EmailMultiAlternatives(
                subject=f"Leave Request: {user.first_name} {user.last_name} - {leave_request.start_date} to {leave_request.end_date}",
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[manager_email],  # Send to manager
                reply_to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)
            
            # Update leave request status
            leave_request.email_sent_to_manager = True
            leave_request.manager_email = manager_email
            leave_request.save(update_fields=['email_sent_to_manager', 'manager_email'])
            
            logger.info(f"Leave request email sent to {manager_email} for {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending leave request email: {str(e)}")
            return False
    
    @staticmethod
    def send_leave_approval_email(leave_request):
        """
        Send email when leave request is approved
        Sends to employee with CC to director
        """
        try:
            user = leave_request.user
            approver = settings.LEAVE_APPROVER
            
            context = {
                'leave_request': leave_request,
                'employee_name': f"{user.first_name} {user.last_name}",
                'approver_name': approver['name'],
                'approver_title': approver['title'],
                'leave_type': leave_request.get_leave_type_display() if hasattr(leave_request, 'get_leave_type_display') else leave_request.leave_type,
                'start_date': leave_request.start_date.strftime('%d-%m-%Y'),
                'end_date': leave_request.end_date.strftime('%d-%m-%Y'),
                'days': (leave_request.end_date - leave_request.start_date).days + 1,
                #'approved_date': leave_request.approved_at.strftime('%d-%m-%Y %H:%M') if leave_request.approved_at else '',
                'leave_request_url': f"{settings.SITE_URL}/leaves/{leave_request.id}/"
            }
            
            html_message = render_to_string('emails/leave_approved.html', context)
            plain_message = strip_tags(html_message)
            
            # Send to employee with director in CC
            email = EmailMultiAlternatives(
                subject=f"Leave Approved: {leave_request.start_date.strftime('%d-%m-%Y')} to {leave_request.end_date.strftime('%d-%m-%Y')}",
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],  # Primary recipient
                cc=[approver['email']]  # Director in CC
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)
            
            leave_request.email_sent_to_employee = True
            leave_request.save(update_fields=['email_sent_to_employee'])
            
            logger.info(f"Leave approval email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending leave approval email: {str(e)}")
            return False
    
    @staticmethod
    def send_leave_rejection_email(leave_request, reason=''):
        """Send email when leave request is rejected"""
        try:
            user = leave_request.user
            
            context = {
                'leave_request': leave_request,
                'employee_name': f"{user.first_name} {user.last_name}",
                'leave_type': leave_request.get_leave_type_display() if hasattr(leave_request, 'get_leave_type_display') else leave_request.leave_type,
                'start_date': leave_request.start_date.strftime('%d-%m-%Y'),
                'end_date': leave_request.end_date.strftime('%d-%m-%Y'),
                'rejection_reason': reason or 'No reason provided',
                'leave_request_url': f"{settings.SITE_URL}/leaves/{leave_request.id}/"
            }
            
            html_message = render_to_string('emails/leave_rejected.html', context)
            plain_message = strip_tags(html_message)
            
            email = EmailMultiAlternatives(
                subject=f"Leave Request Rejected: {leave_request.start_date.strftime('%d-%m-%Y')}",
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)
            
            logger.info(f"Leave rejection email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending leave rejection email: {str(e)}")
            return False
    
    @staticmethod
    def send_leave_status_email(leave_request, old_status, new_status):
        """Send email when leave status changes"""
        try:
            employee = leave_request.employee
            
            context = {
                'leave_request': leave_request,
                'employee_name': f"{employee.first_name} {employee.last_name}",
                'leave_type': leave_request.get_leave_type_display() if hasattr(leave_request, 'get_leave_type_display') else leave_request.leave_type,
                'old_status': old_status,
                'new_status': new_status,
                'start_date': leave_request.start_date.strftime('%d-%m-%Y'),
                'end_date': leave_request.end_date.strftime('%d-%m-%Y'),
                'leave_request_url': f"{settings.SITE_URL}/leaves/{leave_request.id}/"
            }
            
            html_message = render_to_string('emails/leave_status_update.html', context)
            plain_message = strip_tags(html_message)
            
            email = EmailMultiAlternatives(
                subject=f"Leave Status Updated: {new_status}",
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[employee.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)
            
            logger.info(f"Leave status update email sent to {employee.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending leave status email: {str(e)}")
            return False
