from django.urls import path
from .views import request_leave, leave_approvals, team_analytics, leave_calendar, cancel_leave, export_analytics_excel, export_analytics_pdf

urlpatterns = [
    path('request/', request_leave, name='request_leave'),
    path('calendar/', leave_calendar, name='leave_calendar'),
    path('approvals/', leave_approvals, name='leave_approvals'),
    path('analytics/', team_analytics, name='team_analytics'),
    path('cancel-leave/', cancel_leave, name='cancel_leave'),
    # Export functions
    path('analytics/export/excel/', export_analytics_excel, name='export_analytics_excel'),
    path('analytics/export/pdf/', export_analytics_pdf, name='export_analytics_pdf'),
]