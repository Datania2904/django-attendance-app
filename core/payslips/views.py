from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Payslip
from .utils import is_payslip_for_user
from django.contrib import messages

@login_required
def upload_payslips(request):
    profile = request.user.profile

    if profile.role not in ['manager', 'director']:
        return HttpResponseForbidden("You are not allowed")

    if request.method == "POST":
        files = request.FILES.getlist("payslips")
        for f in files:
            Payslip.objects.create(
                uploaded_by=request.user,
                file=f
            )
        messages.success(
            request,
            f"✅ {len(files)} payslip(s) uploaded successfully."
        )
        return redirect("upload_payslips")

    return render(request, "payslips/upload.html")

@login_required
def my_payslips(request):
    profile = request.user.profile

    # Managers & Directors can see all
    if profile.role in ['manager', 'director']:
        payslips = Payslip.objects.all().order_by('-uploaded_at')
    else:
        # Employees: match by filename
        all_payslips = Payslip.objects.all()
        payslips = [
            p for p in all_payslips
            if is_payslip_for_user(p.file.name, request.user)
        ]

    return render(request, "payslips/list.html", {
        "payslips": payslips
    })