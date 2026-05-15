from datetime import date, datetime, timedelta
from calendar import monthrange
from leaves.models import LeaveRequest
from users.models import Profile
from attendance.models import Department
from attendance.utils import get_calendar_data
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
import calendar
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect

@login_required
def calendar_view(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    department_filter = request.GET.get('department', 'all')

    # Validate month/year
    if month < 1 or month > 12:
        month = today.month
    if year < 2000 or year > 2100:
        year = today.year

    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    # Get all employees
    employees = Profile.objects.select_related('user').filter(
        user__is_active=True
    ).order_by('team', 'user__first_name', 'user__last_name')

    # Get all approved leaves
    leaves = LeaveRequest.objects.filter(
        status='approved',
        start_date__lte=last_day,
        end_date__gte=first_day,
        user__is_active=True
    ).values('id', 'user_id', 'start_date', 'end_date', 'leave_type', 'duration')

    leaves_list = list(leaves)

    # Get holidays
    holidays_dict = {}
    # Add your holiday logic here if needed

    # Build leaves by user
    user_leaves = {}
    for leave in leaves_list:
        user_id = leave['user_id']
        if user_id not in user_leaves:
            user_leaves[user_id] = []
        user_leaves[user_id].append(leave)

    calendar_days = list(range(1, last_day.day + 1))

    # Group by team/department
    department_groups = {}
    for emp in employees:
        user = emp.user
        dept_name = emp.team if emp.team else 'No Team'

        if dept_name not in department_groups:
            department_groups[dept_name] = []

        user_data = {
            'user': user,
            'employee_profile': emp,
            'leaves_by_date': {}
        }

        # Build leaves by date for this user
        for day_num in calendar_days:
            current_date = date(year, month, day_num)
            user_data['leaves_by_date'][day_num] = None

            for leave in user_leaves.get(user.id, []):
                if leave['start_date'] <= current_date <= leave['end_date']:
                    leave_key = leave['leave_type']
                    duration = leave.get('duration', 'full')

                    # Map leave type to CSS class
                    leave_class_map = {
                        'Casual': 'casual-leave',
                        'Sick': 'sick-leave',
                        'Earned': 'earned-leave',
                        'Maternity': 'maternity-leave',
                        'WFH': 'work-from-home',
                        'Other': 'other-leave',
                    }

                    leave_type_class = leave_class_map.get(leave_key, 'other-leave')

                    user_data['leaves_by_date'][day_num] = {
                        'type': leave_key,
                        'type_class': leave_type_class,
                        'duration': duration,
                        'id': leave['id']
                    }
                    break

        department_groups[dept_name].append(user_data)

    # Calculate previous/next month
    first_of_month = date(year, month, 1)
    prev_month_date = first_of_month - timedelta(days=1)
    next_month_date = last_day + timedelta(days=1)

    context = {
        'department_groups': department_groups,
        'calendar_days': calendar_days,
        'holidays_dict': holidays_dict,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'prev_month': prev_month_date.month,
        'prev_year': prev_month_date.year,
        'next_month': next_month_date.month,
        'next_year': next_month_date.year,
        'selected_department': department_filter,
        'total_employees': employees.count(),
        'now': timezone.now(),
    }

    return render(request, 'leaves/leave_calendar.html', context)

def get_leave_type_color(leave_type):
    """
    Map LeaveRequest types to colors
    
    Maps: 'paid', 'sick', 'half', 'wfh' to hex colors
    """
    color_map = {
        'paid': '#10b981',   # Green
        'sick': '#ef4444',   # Red
        'half': '#f59e0b',   # Amber
        'wfh': '#3b82f6',    # Blue
    }
    return color_map.get(leave_type, '#6b7280')

@login_required
@require_http_methods(["POST"])
@csrf_protect
def cancel_leave(request):
    """
    Cancel an approved leave request
    - Updates leave status to 'cancelled'
    - Returns used_leaves to available
    - Only the employee who requested or a manager/director can cancel
    """
    
    try:
        # Parse JSON request
        data = json.loads(request.body)
        leave_id = data.get('leave_id')
        
        # Validate input
        if not leave_id:
            return JsonResponse({
                'success': False,
                'message': 'Missing leave_id'
            }, status=400)
        
        # Get the leave request
        try:
            leave = LeaveRequest.objects.get(id=leave_id)
        except LeaveRequest.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Leave request not found'
            }, status=404)
        
        # Security check - Only the employee or manager/director can cancel
        try:
            user_profile = request.user.profile
            is_manager = user_profile.role in ['manager', 'director']
        except:
            is_manager = False
        
        is_own_leave = leave.user == request.user
        
        if not (is_own_leave or is_manager):
            return JsonResponse({
                'success': False,
                'message': 'You do not have permission to cancel this leave'
            }, status=403)
        
        # Check if leave is already approved (can only cancel approved leaves)
        if leave.status != 'approved':
            return JsonResponse({
                'success': False,
                'message': f'Cannot cancel a {leave.status} leave request'
            }, status=400)
        
        # Check if leave date has already passed
        if leave.end_date < date.today():
            return JsonResponse({
                'success': False,
                'message': 'Cannot cancel a leave that has already been completed'
            }, status=400)
        
        # Calculate days that will be cancelled
        def calculate_leave_days(leave_obj):
            """Calculate total days, accounting for half days"""
            total_days = (leave_obj.end_date - leave_obj.start_date).days + 1
            if getattr(leave_obj, "duration", None) in ['first_half', 'second_half']:
                return total_days * 0.5
            return total_days
        
        days_to_cancel = (leave.end_date - leave.start_date).days + 1
        
        # Update leave status
        leave.status = 'cancelled'
        leave.save()
        
        # Prepare response
        return JsonResponse({
            'success': True,
            'message': f'Leave has been cancelled successfully. {days_to_cancel} days returned to available leaves.',
            'leave_id': leave_id,
            'days_returned': days_to_cancel,
            'new_status': 'cancelled'
        }, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON request'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)