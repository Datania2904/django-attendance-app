import os

def is_payslip_for_user(filename, user):
    """
    Match payslip file with user name.
    Order independent.
    """
    name = os.path.basename(filename).lower()

    first = user.first_name.lower()
    last = user.last_name.lower()

    return first in name and last in name
