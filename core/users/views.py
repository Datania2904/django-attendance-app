from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.
from leaves.models import LeaveRequest
from datetime import date
from users.models import Profile
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum

@login_required
def employee_dashboard(request):
    profile = request.user.profile
    today = date.today()
    
    # ============ UPCOMING LEAVES ============
    upcoming_leaves = LeaveRequest.objects.filter(
        user=request.user,
        start_date__gte=today,
        status='approved'
    ).order_by('start_date')
    
    # ============ CALCULATE USED LEAVES (accounting for half days) ============
    def calculate_leave_days(leave_obj):
        """Calculate total days, accounting for half days"""
        total_days = (leave_obj.end_date - leave_obj.start_date).days + 1
        
        # If it's a half day, multiply by 0.5
        if leave_obj.duration in ['first_half', 'second_half']:
            return total_days * 0.5
        
        # Otherwise return full days
        return total_days
    
    # Get all approved leaves and sum the days
    all_approved_leaves = LeaveRequest.objects.filter(
        user=request.user,
        status='approved'
    )
    
    used_leaves = 0
    for leave in all_approved_leaves:
        used_leaves += calculate_leave_days(leave)
    
    # ============ CALCULATE REMAINING LEAVES ============
    # Using the profile.total_leaves (your annual allocation)
    remaining_leaves = profile.total_leaves - used_leaves
    
    # Make sure it doesn't go negative
    remaining_leaves = max(0, remaining_leaves)
    
    # ============ PENDING LEAVES ============
    pending_leaves = LeaveRequest.objects.filter(
        user=request.user,
        status='pending'
    ).count()
    
    # ============ CONTEXT ============
    context = {
        'profile': profile,
        'upcoming_leaves': upcoming_leaves,
        'used_leaves': used_leaves,
        'remaining_leaves': remaining_leaves,
        'pending_leaves': pending_leaves,
        'total_leaves': profile.total_leaves,
    }
    return render(request, 'users/dashboard.html', context)

def home(request):
    return redirect('employee_dashboard')

LEAVE_PER_EMPLOYEE = 20  # yearly leave allocation

@login_required
def teams_view(request):
    from leaves.models import LeaveRequest
    
    # base teams aggregation
    teams = (
        Profile.objects
        .exclude(team__isnull=True)
        .exclude(team__exact='')
        .values('team')
        .annotate(member_count=Count('id'))
        .order_by('team')
    )

    # For each team, compute used/remaining
    for team in teams:
        members = (
            Profile.objects
            .filter(team=team['team'])
            .select_related('user')
        )

        team_total_leaves = members.count() * LEAVE_PER_EMPLOYEE
        team_used = 0

        # Compute per-member stats
        for member in members:
            # Attach the properties (which now use half-day logic)
            member_used = member.used_leaves      # Property - half-day aware
            member_remaining = member.remaining_leaves  # Property - half-day aware
            
            # Calculate pending days with half-day support
            pending_leaves_qs = LeaveRequest.objects.filter(
                user=member.user,
                status='pending'
            )
            pending_days = 0
            for leave in pending_leaves_qs:
                total_days = (leave.end_date - leave.start_date).days + 1
                if getattr(leave, "duration", None) in ['first_half', 'second_half']:
                    pending_days += total_days * 0.5
                else:
                    pending_days += total_days
            
            member.pending_leaves = pending_days
            team_used += member_used

        team['total_leaves'] = team_total_leaves
        team['used_leaves'] = team_used
        team['remaining_leaves'] = max(team_total_leaves - team_used, 0)
        team['members'] = members

    team_members = (
        Profile.objects
        .select_related('user')
        .order_by('team', 'user__first_name')
    )

    context = {
        'teams': teams,
        'team_members': team_members
    }

    return render(request, 'users/teams.html', context)