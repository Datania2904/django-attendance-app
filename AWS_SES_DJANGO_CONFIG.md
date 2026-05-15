# 🔧 AWS SES Django Configuration - Complete Setup

## Prerequisites

You should have from AWS SES setup:
- SMTP Server: `email-smtp.ap-south-1.amazonaws.com` (or your region)
- SMTP Username: (from credentials)
- SMTP Password: (from credentials)
- Verified Email: `noreply@yourcompany.com`

---

## Step 1: Install Required Package

```bash
pip install python-dotenv
```

This allows Django to read credentials from `.env` file (secure).

---

## Step 2: Create .env File

Create file: `.env` (in your project root, same folder as `manage.py`)

```env
# AWS SES SMTP Credentials
SES_SMTP_USER=YOUR_SMTP_USERNAME_HERE
SES_SMTP_PASS=YOUR_SMTP_PASSWORD_HERE
SES_REGION=ap-south-1
SES_FROM_EMAIL=noreply@yourcompany.com
LEAVE_MANAGER_EMAIL=manager@yourcompany.com
```

Replace:
- `YOUR_SMTP_USERNAME_HERE` - with your actual SMTP username
- `YOUR_SMTP_PASSWORD_HERE` - with your actual SMTP password
- `ap-south-1` - with your AWS region
- `noreply@yourcompany.com` - with your verified email
- `manager@yourcompany.com` - with your manager's email

---

## Step 3: Update .gitignore

Make sure `.env` is NOT committed to git:

Add to `.gitignore`:
```
.env
*.pyc
__pycache__/
```

---

## Step 4: Update settings.py

**Complete settings.py email configuration:**

```python
# settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

# ============================================
# AWS SES EMAIL CONFIGURATION
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# AWS SES SMTP settings
EMAIL_HOST = f"email-smtp.{os.getenv('SES_REGION', 'ap-south-1')}.amazonaws.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# AWS SES SMTP credentials (from .env)
EMAIL_HOST_USER = os.getenv('SES_SMTP_USER')
EMAIL_HOST_PASSWORD = os.getenv('SES_SMTP_PASS')

# From email (must be verified in SES)
DEFAULT_FROM_EMAIL = os.getenv('SES_FROM_EMAIL', 'noreply@example.com')
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Leave Management
LEAVE_MANAGER_EMAIL = os.getenv('LEAVE_MANAGER_EMAIL', 'manager@example.com')

# Optional: Email logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Step 5: Update Your Email Service (No Changes Needed!)

Your existing `leaves/services/email_service.py` works as-is!

The signal handler and email service don't need changes. Just test:

```python
# Example from your current email_service.py
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

@staticmethod
def send_leave_request_email(leave_request):
    context = {
        'employee_name': f"{leave_request.user.first_name} {leave_request.user.last_name}",
        'start_date': leave_request.start_date.strftime('%d-%m-%Y'),
        'end_date': leave_request.end_date.strftime('%d-%m-%Y'),
        # ... other fields
    }
    
    html_message = render_to_string('emails/leave_request.html', context)
    
    email = EmailMessage(
        subject=f"New Leave Request: {leave_request.user.get_full_name()}",
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,  # This now uses AWS SES
        to=[settings.LEAVE_MANAGER_EMAIL]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
    
    return True
```

✅ **No code changes needed** - just configuration!

---

## Step 6: Test AWS SES Connection

```bash
python manage.py shell
```

Run this test:

```python
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials from .env
smtp_user = os.getenv('SES_SMTP_USER')
smtp_pass = os.getenv('SES_SMTP_PASS')
smtp_host = f"email-smtp.{os.getenv('SES_REGION', 'ap-south-1')}.amazonaws.com"
smtp_port = 587

print(f"Testing AWS SES Connection...")
print(f"Host: {smtp_host}")
print(f"Port: {smtp_port}")
print(f"User: {smtp_user[:20]}...")  # Show first 20 chars only

try:
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_pass)
    print("✅ AWS SES SMTP Connection Successful!")
    server.quit()
except Exception as e:
    print(f"❌ Connection Failed: {e}")
```

**Expected output:**
```
Testing AWS SES Connection...
Host: email-smtp.ap-south-1.amazonaws.com
Port: 587
User: AKIA...
✅ AWS SES SMTP Connection Successful!
```

---

## Step 7: Test Sending Email via Django

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

print(f"From: {settings.DEFAULT_FROM_EMAIL}")
print(f"To: test@example.com")

try:
    send_mail(
        subject='Test Email from AWS SES',
        message='This is a test email via AWS SES SMTP.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['your.personal@gmail.com'],  # Use real email to test
        fail_silently=False,
    )
    print("✅ Email sent successfully via AWS SES!")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
```

**Expected output:**
```
From: noreply@yourcompany.com
To: your.personal@gmail.com
✅ Email sent successfully via AWS SES!
```

Check your email inbox - you should receive the test email!

---

## Step 8: Test with Your Existing Code

Now test with your actual leave request:

```bash
python manage.py shell
```

```python
from leaves.models import LeaveRequest
from django.contrib.auth.models import User
from datetime import date, timedelta

user = User.objects.first()

# Create a leave request (should trigger signal and send email)
leave = LeaveRequest.objects.create(
    user=user,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=2),
    leave_type='Casual',
    duration='full',
    reason='Test leave via SES',
    status='pending'
)

print(f"✅ Leave request created: {leave.id}")
print("Check your manager's email inbox for the leave request email")
```

Check your manager's email - you should see the leave request notification!

---

## 🚨 Common Issues & Fixes

### Issue 1: "Authentication unsuccessful"
**Problem:** Wrong SMTP credentials
**Fix:**
- Double-check .env file has correct username and password
- Make sure credentials are exact (no extra spaces)
- Delete old SMTP credentials in AWS and create new ones

### Issue 2: "Email address is not verified"
**Problem:** Sending from email that's not verified in SES
**Fix:**
- Verify the email in AWS SES console
- Wait for verification email and click link
- Update DEFAULT_FROM_EMAIL to verified email

### Issue 3: "Can only send to verified emails"
**Problem:** SES account still in Sandbox
**Fix:**
- Request production access in SES console
- Or verify recipient emails in SES (for sandbox testing)
- Usually takes 24 hours for production approval

### Issue 4: "Connection timed out"
**Problem:** SMTP host or port wrong
**Fix:**
- Check your AWS region
- Verify SMTP host format: `email-smtp.REGION.amazonaws.com`
- Port should be 587 (not 25 or 465)

### Issue 5: ".env file not found"
**Problem:** python-dotenv not installed or .env in wrong location
**Fix:**
- Install: `pip install python-dotenv`
- .env must be in project root (same folder as manage.py)
- Make sure file is named `.env` exactly

---

## 📋 Complete Checklist

- [ ] AWS Account created
- [ ] SES region chosen (ap-south-1)
- [ ] Email verified in SES console
- [ ] SMTP credentials created
- [ ] Credentials copied to .env file
- [ ] .env added to .gitignore
- [ ] settings.py updated with SES config
- [ ] python-dotenv installed
- [ ] SMTP test connection successful
- [ ] Django send_mail test successful
- [ ] Leave request email test successful

---

## ✅ You're All Set!

Your Django project is now configured to send emails via AWS SES!

**What changed:**
- Office365 SMTP → AWS SES SMTP
- Office365 credentials → AWS SES credentials
- No code changes to email service or signals

**What stays the same:**
- Email service class (email_service.py)
- Signal handlers (signals.py)
- Email templates
- Your existing views and models

---

## 📁 Files to Keep

- `.env` - Contains AWS SES credentials (keep private!)
- `settings.py` - Updated with SES config
- `leaves/signals.py` - No changes
- `leaves/services/email_service.py` - No changes
- `.gitignore` - Added .env

---

## 🎉 Success Indicators

✅ SMTP connection test passes
✅ Django send_mail test sends email
✅ Leave request email sent to manager
✅ Email received in inbox
✅ No authentication errors

If all ✅, you're done! Deploy and enjoy reliable AWS SES email service! 🚀

