from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Department, EmployeeProfile, Holiday

# Register your models here.
admin.site.register(Holiday)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_count', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']

    def employee_count(self, obj):
        count = obj.employees.filter(is_active=True).count()
        return format_html(
            '<span style="background-color: #e3f2fd; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            count
        )
    employee_count.short_description = 'Active Employees'


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'employee_id', 'department', 'is_active', 'hire_date']
    list_filter = ['department', 'is_active', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email']
    ordering = ['user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Employee Details', {
            'fields': ('employee_id', 'department', 'phone', 'hire_date', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Employee Name'


    def color_display(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px; display: inline-block;"></div> {}',
            obj.color_code,
            obj.color_code
        )
    color_display.short_description = 'Color'

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 100px; height: 50px; background-color: {}; border-radius: 5px; border: 1px solid #ccc;"></div>',
            obj.color_code
        )
    color_preview.short_description = 'Color Preview'



    def get_employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username
    get_employee_name.short_description = 'Employee'

    def get_dates(self, obj):
        return f"{obj.start_date} to {obj.end_date}"
    get_dates.short_description = 'Period'

    def status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'approved': '#10b981',
            'rejected': '#ef4444',
            'cancelled': '#6b7280'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def number_of_days_display(self, obj):
        return obj.number_of_days
    number_of_days_display.short_description = 'Number of Days'

    def approve_absences(self, request, queryset):
        updated = 0
        for absence in queryset.filter(status='pending'):
            absence.approve(request.user, 'Approved via admin bulk action')
            updated += 1
        self.message_user(request, f'{updated} absence(s) approved.')
    approve_absences.short_description = 'Approve selected absences'

    def reject_absences(self, request, queryset):
        updated = 0
        for absence in queryset.filter(status='pending'):
            absence.reject(request.user, 'Rejected via admin bulk action')
            updated += 1
        self.message_user(request, f'{updated} absence(s) rejected.')
    reject_absences.short_description = 'Reject selected absences'

    def mark_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} absence(s) marked as pending.')
    mark_pending.short_description = 'Mark selected as pending'
