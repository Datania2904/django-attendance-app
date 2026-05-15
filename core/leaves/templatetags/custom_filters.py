from django import template
from datetime import date

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary using key"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.simple_tag
def get_date_weekday(day, year, month):
    """
    Get weekday number for a specific date
    Returns: 0=Monday, 1=Tuesday, ... 5=Saturday, 6=Sunday
    Usage in template: {% get_date_weekday day year month as weekday %}
    """
    try:
        target_date = date(int(year), int(month), int(day))
        return target_date.weekday()
    except (ValueError, TypeError):
        return 0
