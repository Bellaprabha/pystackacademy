import razorpay
import json
import hmac
import hashlib

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from django.core.mail import EmailMessage
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, TruncDay

from io import BytesIO
from reportlab.pdfgen import canvas
from accounts.decorators import admin_required

from .models import Payment
from courses.models import Course, Enrollment


# ==============================
# 🧾 GENERATE PDF INVOICE
# ==============================
def generate_invoice_pdf(payment):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    amount = float(payment.amount)
    gst = amount * 0.18
    base = amount - gst

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, "PyStack Academy - GST Invoice")

    p.setFont("Helvetica", 11)
    p.drawString(100, 770, f"User: {payment.user.username}")
    p.drawString(100, 750, f"Course: {payment.course_name}")

    p.drawString(100, 720, f"Base Amount: ₹{round(base,2)}")
    p.drawString(100, 700, f"GST (18%): ₹{round(gst,2)}")
    p.drawString(100, 680, f"Total Amount: ₹{amount}")

    p.drawString(100, 650, f"Payment ID: {payment.payment_id}")
    p.drawString(100, 630, f"Date: {payment.created_at.strftime('%d-%m-%Y %H:%M')}")

    p.drawString(100, 600, "GST No: 29ABCDE1234F2Z5")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer


# ==============================
# 💳 CREATE PAYMENT
# ==============================
@login_required
def create_payment(request, course_id):
    course = Course.objects.get(id=course_id)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    amount = int(course.price * 100)  # paise

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    Payment.objects.create(
        user=request.user,
        course_name=course.title,
        amount=course.price,
        order_id=order['id'],
        status="created"
    )

    return render(request, "payments/payment.html", {
        "order_id": order['id'],
        "amount": amount,
        "display_amount": course.price,
        "key": settings.RAZORPAY_KEY_ID,
        "course": course
    })


# ==============================
# ✅ VERIFY PAYMENT
# ==============================
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })
        except Exception:
            return HttpResponse("FAIL")

        try:
            payment = Payment.objects.get(order_id=order_id)

            payment.payment_id = payment_id
            payment.status = "success"
            payment.save()

            course = Course.objects.get(title=payment.course_name)

            if not Enrollment.objects.filter(user=payment.user, course=course).exists():
                Enrollment.objects.create(
                    user=payment.user,
                    name=payment.user.username,
                    phone="0000000000",
                    course=course,
                    is_verified=True
                )

            # 📩 EMAIL WITH PDF
            try:
                pdf = generate_invoice_pdf(payment)

                email = EmailMessage(
                    subject="Payment Successful - Invoice",
                    body=f"Hello {payment.user.username},\n\nPayment successful!",
                    from_email=settings.EMAIL_HOST_USER,
                    to=[payment.user.email],
                )

                email.attach(f"invoice_{payment.id}.pdf", pdf.read(), 'application/pdf')
                email.send()

            except Exception as e:
                print("Email Error:", e)

            return HttpResponse("OK")

        except Exception as e:
            print("Payment Error:", e)
            return HttpResponse("FAIL")


# ==============================
# ✅ SUCCESS / FAILURE
# ==============================
def payment_success(request):
    return render(request, 'payments/success.html')


def payment_failure(request):
    course_id = request.GET.get('course_id')
    return render(request, 'payments/failure.html', {'course_id': course_id})


# ==============================
# 📜 USER PAYMENT HISTORY
# ==============================
@login_required
def payment_history(request):
    status = request.GET.get('status')

    payments = Payment.objects.filter(user=request.user)

    if status == "success":
        payments = payments.filter(status="success")
    elif status == "failed":
        payments = payments.filter(status="failed")

    return render(request, 'payments/payment_history.html', {
        'payments': payments.order_by('-created_at')
    })


# ==============================
# 📄 DOWNLOAD INVOICE
# ==============================
@login_required
def download_invoice(request, payment_id):
    payment = Payment.objects.get(id=payment_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{payment.id}.pdf"'

    pdf = generate_invoice_pdf(payment)
    response.write(pdf.read())

    return response


# ==============================
# 📊 USER DASHBOARD
# ==============================
@login_required
def payment_dashboard(request):
    payments = Payment.objects.filter(user=request.user)

    total = payments.count()
    success = payments.filter(status="success").count()

    total_revenue = payments.filter(status="success").aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    success_rate = (success / total * 100) if total else 0

    return render(request, "payments/dashboard.html", {
        "total": total,
        "success": success,
        "total_revenue": total_revenue,
        "success_rate": round(success_rate, 2)
    })


# ==============================
# 🔐 WEBHOOK (SECURE)
# ==============================
@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        body = request.body
        signature = request.headers.get('X-Razorpay-Signature')

        generated = hmac.new(
            bytes(settings.RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        if generated != signature:
            return HttpResponse(status=400)

        return HttpResponse(status=200)


# ==============================
# 👨‍💼 ADMIN DASHBOARD (PROTECTED)
# ==============================
# @staff_member_required
# def admin_dashboard(request):
@admin_required
def admin_dashboard(request):
    payments = Payment.objects.all()

    total_revenue = payments.filter(status="success").aggregate(
        Sum('amount')
    )['amount__sum'] or 0

    return render(request, "payments/admin_dashboard.html", {
        "total_revenue": total_revenue,
        "success_count": payments.filter(status="success").count(),
        "failed_count": payments.filter(status="failed").count()
    })


# ==============================
# 📊 CHARTS
# ==============================
def revenue_chart(request):
    data = (
        Payment.objects.filter(status="success")
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    return render(request, "payments/chart.html", {"data": data})


def payment_pie_chart(request):
    data = Payment.objects.values('status').annotate(count=Count('id'))

    return render(request, "payments/pie_chart.html", {
        "labels": [d['status'] for d in data],
        "values": [d['count'] for d in data]
    })


def daily_revenue(request):
    data = (
        Payment.objects.filter(status="success")
        .annotate(day=TruncDay('created_at'))
        .values('day')
        .annotate(total=Sum('amount'))
        .order_by('day')
    )
    return render(request, "payments/daily_chart.html", {"data": data})


# ==============================
# 📤 EXPORT EXCEL
# ==============================
def export_excel(request):
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Payments"

    ws.append(["User", "Course", "Amount", "Status", "Date"])

    for p in Payment.objects.all():
        ws.append([
            p.user.username,
            p.course_name,
            p.amount,
            p.status,
            str(p.created_at)
        ])

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="payments.xlsx"'

    wb.save(response)
    return response

from django.http import JsonResponse

def dashboard_data(request):
    payments = Payment.objects.filter(status="success")

    total = payments.count()
    revenue = sum(p.amount for p in payments)

    return JsonResponse({
        "total": total,
        "revenue": revenue
    })

from django.http import JsonResponse

def dashboard_data(request):
    payments = Payment.objects.filter(status="success")

    return JsonResponse({
        "total": payments.count(),
        "revenue": sum(p.amount for p in payments)
    })