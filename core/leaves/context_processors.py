from leaves.models import LeaveRequest

def pending_approvals_count(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "profile") and request.user.profile.role in ["manager", "director"]:
            pending_count = LeaveRequest.objects.filter(status="pending").count()
        else:
            pending_count = 0
    else:
        pending_count = 0

    return {
        "pending_approvals_count": pending_count
    }
