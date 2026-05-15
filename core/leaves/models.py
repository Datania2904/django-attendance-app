from django.db import models
from django.contrib.auth.models import User

class LeaveRequest(models.Model):
    LEAVE_TYPE = (
        ('Casual', 'Casual Leave'),
        ('Sick', 'Sick Leave'),
        ('Earned', 'Earned Leave'),
        ('Maternity', 'WMaternity Leave'),
        ('WFH', 'Work From Home'),
        ('Other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    DURATION_CHOICES = (
        ('full', 'Full Day'),
        ('first_half', 'First Half'),
        ('second_half', 'Second Half'),
    )

    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='full')
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="created_leave_requests")
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)

    employee = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True, related_name="employee_leave_requests")
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)

        # Email tracking
    email_sent_to_manager = models.BooleanField(default=False)
    email_sent_to_employee = models.BooleanField(default=False)
    manager_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.start_date} to {self.end_date} ({self.get_duration_display()})"
    
    @property
    def total_days(self):
        """Calculate total days, accounting for half days"""
        base_days = (self.end_date - self.start_date).days + 1
        
        # If it's a half day, count as 0.5 days
        if self.duration in ['first_half', 'second_half']:
            return base_days * 0.5
        
        # Otherwise full days
        return base_days