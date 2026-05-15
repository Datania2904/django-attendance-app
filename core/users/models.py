from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    ROLE_CHOICES = (
        ('employee', 'Employee'),
        ('manager', 'Manager'),
        ('director', 'Director'),
    )

    TEAM_CHOICES = (
        ('Tech', 'Tech'),
        ('DCM', 'DCM'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    team = models.CharField(max_length=50)

    total_leaves = models.IntegerField(default=20)
    used_leaves = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} ({self.team})"

    """def remaining_leaves(self):
        return self.total_leaves - self.used_leaves"""

    def _calculate_leave_days(self, leave_obj):
        """Helper: calculate days with half-day support"""
        total_days = (leave_obj.end_date - leave_obj.start_date).days + 1
        if getattr(leave_obj, "duration", None) in ['first_half', 'second_half']:
            return total_days * 0.5
        return total_days

    @property
    def used_leaves(self):
        """Override used_leaves to account for half days"""
        from leaves.models import LeaveRequest
        approved = LeaveRequest.objects.filter(user=self.user, status='approved')
        days = 0
        for leave in approved:
            days += self._calculate_leave_days(leave)
        return days

    @property
    def remaining_leaves(self):
        """Override remaining_leaves to account for half days"""
        remaining = self.total_leaves - self.used_leaves
        return max(0, remaining)