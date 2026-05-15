# ⚡ AWS SES Setup - Quick Summary (Copy-Paste Ready)

## 🎯 What You Need to Do

### 1. AWS SES Setup (5 minutes)

**Go to:** https://console.aws.amazon.com/

**Steps:**
1. Search for **SES** → Click **Simple Email Service**
2. Make sure region is **ap-south-1** (top right)
3. Left menu → **Verified Identities** → **Create Identity** → Email
4. Enter: `noreply@yourcompany.com`
5. Verify the email (check your inbox for verification link)
6. Left menu → **SMTP Settings**
7. Note down SMTP server: `email-smtp.ap-south-1.amazonaws.com`
8. Click **Create SMTP Credentials**
9. Create user (default name is fine)
10. **COPY the SMTP Username and Password** (you'll only see once)

---

### 2. Django Setup (5 minutes)

**Step 1: Install package**
```bash
pip install python-dotenv
```

**Step 2: Create .env file**

Create file `.env` in your project root (same folder as manage.py):

```env
SES_SMTP_USER=PASTE_YOUR_SMTP_USERNAME_HERE
SES_SMTP_PASS=PASTE_YOUR_SMTP_PASSWORD_HERE
SES_REGION=ap-south-1
SES_FROM_EMAIL=noreply@yourcompany.com
LEAVE_MANAGER_EMAIL=manager@yourcompany.com
```

**Step 3: Update settings.py**

Copy this into your `settings.py`:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

# === AWS SES EMAIL ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = f"email-smtp.{os.getenv('SES_REGION', 'ap-south-1')}.amazonaws.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('SES_SMTP_USER')
EMAIL_HOST_PASSWORD = os.getenv('SES_SMTP_PASS')
DEFAULT_FROM_EMAIL = os.getenv('SES_FROM_EMAIL')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
LEAVE_MANAGER_EMAIL = os.getenv('LEAVE_MANAGER_EMAIL')
```

**Step 4: Update .gitignore**

Add to `.gitignore`:
```
.env
```

---

### 3. Test (2 minutes)

**Test SMTP connection:**

```bash
python manage.py shell
```

```python
import smtplib, os
from dotenv import load_dotenv

load_dotenv()

host = f"email-smtp.{os.getenv('SES_REGION', 'ap-south-1')}.amazonaws.com"
user = os.getenv('SES_SMTP_USER')
password = os.getenv('SES_SMTP_PASS')

try:
    server = smtplib.SMTP(host, 587)
    server.starttls()
    server.login(user, password)
    print("✅ AWS SES SMTP Works!")
    server.quit()
except Exception as e:
    print(f"❌ Error: {e}")
```

Expected: `✅ AWS SES SMTP Works!`

---

**Test sending email:**

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test from AWS SES',
    message='This is a test email',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your.email@gmail.com'],
    fail_silently=False,
)
print("✅ Email sent!")
```

Check your email inbox - you should receive it!

---

**Test with actual leave request:**

```bash
python manage.py shell
```

```python
from leaves.models import LeaveRequest
from django.contrib.auth.models import User
from datetime import date, timedelta

user = User.objects.first()
leave = LeaveRequest.objects.create(
    user=user,
    start_date=date.today(),
    end_date=date.today() + timedelta(days=2),
    leave_type='Casual',
    duration='full',
    reason='Test',
    status='pending'
)
print("✅ Leave created - check manager email!")
```

---

## 📋 Complete File Listing

### .env file (Project Root)
```env
SES_SMTP_USER=AKIAIOSFODNN7EXAMPLE
SES_SMTP_PASS=BpuK...YourLongPassword...WxQp
SES_REGION=ap-south-1
SES_FROM_EMAIL=noreply@yourcompany.com
LEAVE_MANAGER_EMAIL=manager@yourcompany.com
```

### settings.py (Email section)
```python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = f"email-smtp.{os.getenv('SES_REGION', 'ap-south-1')}.amazonaws.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('SES_SMTP_USER')
EMAIL_HOST_PASSWORD = os.getenv('SES_SMTP_PASS')
DEFAULT_FROM_EMAIL = os.getenv('SES_FROM_EMAIL')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
LEAVE_MANAGER_EMAIL = os.getenv('LEAVE_MANAGER_EMAIL')
```

### .gitignore (updated)
```
.env
*.pyc
__pycache__/
```

---

## ✅ Checklist

- [ ] AWS SES email verified
- [ ] SMTP credentials created and copied
- [ ] .env file created with credentials
- [ ] python-dotenv installed
- [ ] settings.py updated
- [ ] .gitignore updated
- [ ] SMTP test passes
- [ ] send_mail test succeeds
- [ ] Leave request email test succeeds

---

## 🎉 Done!

Your Django project now uses AWS SES for reliable email sending!

**No code changes needed** to:
- signals.py
- email_service.py
- email templates
- views.py

Just configuration! Everything else stays the same.

---

## ❓ Still Having Issues?

### "Email address not verified"
→ Check SES console, verify email, click link in email

### "Authentication unsuccessful"  
→ Check .env has correct username and password, no extra spaces

### "Can only send to verified emails"
→ Request production access in SES console (usually 24 hours)

### "Connection timeout"
→ Check region is correct: ap-south-1 for India, us-east-1 for US

---

## 🔗 Useful Links

- AWS SES Console: https://console.aws.amazon.com/
- SES Documentation: https://docs.aws.amazon.com/ses/
- SMTP Credentials: https://docs.aws.amazon.com/ses/latest/dg/smtp-credentials.html

---

**Ready to send emails via AWS SES! 🚀**

