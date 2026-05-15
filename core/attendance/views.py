from datetime import date, datetime, timedelta
from calendar import monthrange
from leaves.models import LeaveRequest
from users.models import Profile
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
@login_required
def calendar_view(request):
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))

    first_day = date(year, month, 1)
    days_in_month = monthrange(year, month)[1]

    calendar_days = []
    #calendar_days = get_calendar_data(request.user, year, month)

    profile = Profile.objects.get(user=request.user)

    if profile.role in ['manager', 'director']:
        leaves = LeaveRequest.objects.filter(
            start_date__year=year,
            start_date__month=month
        )
    else:
        leaves = LeaveRequest.objects.filter(
            start_date__year=year,
            start_date__month=month
        )

    for day in range(1, days_in_month + 1):
        current_date = date(year, month, day)
        day_leaves = leaves.filter(
            start_date__lte=current_date,
            end_date__gte=current_date
        )

        calendar_days.append({
            'date': current_date,
            'day': day,
            'leaves': day_leaves
        })

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1

    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'calendar_days': calendar_days,
        'month': first_day.strftime('%B'),
        'year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'role': profile.role,
    }

    return render(request, 'attendance/calendar.html', context)

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