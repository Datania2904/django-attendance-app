from leaves.models import LeaveRequest

def approval_counts(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "profile") and request.user.profile.role in ["manager", "director"]:
            pending_count = LeaveRequest.objects.filter(status="pending",user=request.user).count()
        else:
            pending_count = 0
    else:
        pending_count = 0

    return {
        "pending_approvals_count": pending_count
    }
