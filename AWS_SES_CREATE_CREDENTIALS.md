# 📧 AWS SES SMTP Credentials - Complete Step-by-Step Setup

## Overview

AWS SES requires **separate SMTP credentials** (different from IAM keys). Follow these steps to create them.

---

## ✅ Prerequisites

- Active AWS Account (with billing enabled)
- Email address you want to verify (e.g., `noreply@yourcompany.com` or your personal email)
- Access to that email inbox (to verify it)

---

## 🔑 Step 1: Go to AWS SES Console

1. **Login to AWS Console:**
   - Go to: https://console.aws.amazon.com/
   - Sign in with your AWS account

2. **Navigate to SES:**
   - In search bar, search: `SES` or `Simple Email Service`
   - Click on **Simple Email Service**

3. **Check Your Region:**
   - Look at top-right corner
   - Choose region closest to you (for India: **ap-south-1**)
   - *Important: SES is not available in all regions*
   - Available regions: `us-east-1`, `us-west-2`, `eu-west-1`, `ap-south-1`, etc.

   **⚠️ If your region doesn't show SES, switch region and try again**

---

## ✉️ Step 2: Verify Your Sender Email Address

**You MUST verify the email address before sending.**

1. **In SES Dashboard, click:**
   - Left menu → **Email Addresses** (or **Verified Identities**)

2. **Click "Verify a New Email Address"**

3. **Enter your email:**
   - Example: `noreply@yourcompany.com` or `your.personal@gmail.com`
   - Click **Verify This Email Address**

4. **Check your email inbox:**
   - AWS sends verification email
   - Click the verification link in the email
   - You'll see: "Email address verified successfully"

5. **Back in SES console:**
   - Your email now shows status: **verified** ✓

**✅ Email is now verified and can be used as sender**

---

## 🔐 Step 3: Create SMTP Credentials

Now create the special SMTP username and password:

1. **In SES Dashboard, click:**
   - Left menu → **SMTP Settings**

2. **You'll see:**
   - SMTP server endpoint (like `email-smtp.ap-south-1.amazonaws.com`)
   - Port information (25, 465, 587)
   - Copy this SMTP server name (you'll need it for Django)

3. **Click: "Create SMTP Credentials"**
   - (Button is usually at top of SMTP Settings page)

4. **Create IAM user for SMTP:**
   - A dialog appears asking for IAM username
   - Keep default or change to something like: `ses-smtp-user`
   - Click **Create**

5. **AWS creates credentials and shows:**
   ```
   SMTP Username: [long string like: AKIAIOSFODNN7EXAMPLE]
   SMTP Password: [another long string]
   ```
   
   **⚠️ IMPORTANT: Copy both values NOW**
   - You can only see the password ONCE
   - If you lose it, you must delete and recreate

6. **Click "Download Credentials"**
   - This downloads a .csv file with your credentials
   - Save it safely (but keep it private!)

---

## 📝 Step 4: Write Down Your Credentials

Create a text file or note with these values:

```
AWS SES SMTP CREDENTIALS
========================

Region: ap-south-1
SMTP Server: email-smtp.ap-south-1.amazonaws.com
Port: 587
Encryption: STARTTLS (TLS)

SMTP Username: [paste the username]
SMTP Password: [paste the password]

Verified Email: noreply@yourcompany.com
```

**Keep this file safe and private!**

---

## 🧪 Step 5: Test SMTP Connection (Before Django)

Let's verify these credentials work:

### On Windows (using PowerShell):

```powershell
$emailUser = "YOUR_SMTP_USERNAME"
$emailPass = "YOUR_SMTP_PASSWORD"
$emailHost = "email-smtp.ap-south-1.amazonaws.com"
$emailPort = 587

# Create SMTP object
$SMTPClient = New-Object Net.Mail.SmtpClient($emailHost, $emailPort)
$SMTPClient.EnableSsl = $true
$SMTPClient.Credentials = New-Object System.Net.NetworkCredential("$emailUser", "$emailPass")

# Try to connect
try {
    $SMTPClient.SendAsync()
    Write-Host "✅ SMTP Connection successful!"
} catch {
    Write-Host "❌ Connection failed: $_"
}
```

### On Linux/Mac (using Python):

```bash
python3 << EOF
import smtplib

email_user = "YOUR_SMTP_USERNAME"
email_pass = "YOUR_SMTP_PASSWORD"
email_host = "email-smtp.ap-south-1.amazonaws.com"
email_port = 587

try:
    server = smtplib.SMTP(email_host, email_port)
    server.starttls()
    server.login(email_user, email_pass)
    print("✅ SMTP Connection successful!")
    server.quit()
except Exception as e:
    print(f"❌ Connection failed: {e}")
EOF
```

**Expected output:**
```
✅ SMTP Connection successful!
```

If successful, your credentials are correct! ✓

---

## 🚨 Step 6: Common Issues & Fixes

### Issue 1: "No verified identities"
**Problem:** Haven't verified any email yet
**Fix:** Go to Email Addresses, verify an email, and wait for verification email

### Issue 2: "SMTP Credentials button not visible"
**Problem:** Can't find the Create SMTP Credentials button
**Fix:** 
- Make sure you're in the correct region (has SES)
- Refresh the page
- Try different browser

### Issue 3: "Authentication failed"
**Problem:** Username/password incorrect or credentials expired
**Fix:**
- Double-check credentials match exactly (copy-paste to be sure)
- Delete and recreate SMTP credentials
- Make sure you copied the entire username (sometimes long)

### Issue 4: "Can only send to verified emails"
**Problem:** SES still in Sandbox mode
**Fix:** Request Production Access in SES
- In SES Dashboard, look for "Sending Limits"
- Click "Edit" next to "Account Details"
- Request production access (explain you need it for business emails)
- AWS approves (usually within 24 hours)

---

## 📊 What You Now Have

| Item | Value | Use In Django |
|------|-------|----------------|
| SMTP Server | email-smtp.ap-south-1.amazonaws.com | `EMAIL_HOST` |
| Port | 587 | `EMAIL_PORT` |
| Encryption | STARTTLS | `EMAIL_USE_TLS = True` |
| Username | [copied above] | `EMAIL_HOST_USER` |
| Password | [copied above] | `EMAIL_HOST_PASSWORD` |
| From Email | noreply@yourcompany.com | `DEFAULT_FROM_EMAIL` |

---

## ✅ Quick Checklist

- [ ] AWS Account created and accessible
- [ ] Region chosen (ap-south-1 for India, us-east-1 for US)
- [ ] Email verified in SES
- [ ] SMTP Credentials created
- [ ] Credentials downloaded/copied
- [ ] Tested SMTP connection (works)
- [ ] Ready to use in Django

---

## 🎯 Next Steps

After credentials are created:

1. Create `.env` file in Django project
2. Add credentials to `.env`
3. Update Django `settings.py` with SES config
4. Test sending emails from Django
5. Deploy!

**See: `AWS_SES_DJANGO_CONFIG.md` for Django setup**

---

## 📞 Need Help?

| Issue | Resource |
|-------|----------|
| SES not in region | https://aws.amazon.com/ses/ - check available regions |
| Email verification stuck | Check spam folder, resend verification |
| Sandbox limitations | https://docs.aws.amazon.com/ses/latest/dg/request-production-access.html |
| SMTP credentials lost | Delete and recreate them |

---

**Congratulations! You now have AWS SES SMTP credentials ready to use!** 🎉

Next: Configure Django to use these credentials.

