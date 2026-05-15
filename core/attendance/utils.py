from datetime import date, timedelta
from leaves.models import LeaveRequest
from attendance.models import Holiday, Shift

def get_calendar_data(user, year, month):
    first_day = date(year, month, 1)
    last_day = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    days = []

    holidays = {h.date: h.name for h in Holiday.objects.all()}
    leaves = LeaveRequest.objects.filter(user=user)
    shifts = Shift.objects.filter(user=user)

    for i in range((last_day - first_day).days + 1):
        current = first_day + timedelta(days=i)

        day_info = {
            'date': current,
            'label': '',
            'color': 'white'
        }

        # 🟣 Holiday
        if current in holidays:
            day_info['label'] = holidays[current]
            day_info['color'] = 'purple'

        # 🔴 Approved Leave
        for leave in leaves:
            if leave.start_date <= current <= leave.end_date:
                if leave.status == 'approved':
                    day_info['label'] = 'Leave (Approved)'
                    day_info['color'] = 'red'
                elif leave.status == 'pending':
                    day_info['label'] = 'Leave (Pending)'
                    day_info['color'] = 'yellow'

        # 🔵 Shift
        for shift in shifts:
            if shift.date == current:
                day_info['label'] = shift.get_shift_type_display()
                day_info['color'] = 'blue'

        # ⚫ Weekend (only if nothing else applied)
        if current.weekday() >= 5 and day_info['color'] == 'white':
            day_info['color'] = 'lightgray'
            day_info['label'] = 'Weekend'

        days.append(day_info)

    return days
