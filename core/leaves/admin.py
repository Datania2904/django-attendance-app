from django.contrib import admin

# Register your models here.
from .models import LeaveRequest
admin.site.register(LeaveRequest)