import razorpay
import json

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Payment
from courses.models import Course, Enrollment
from django.contrib.auth.decorators import login_required


# ✅ CREATE PAYMENT
def create_payment(request, course_id):
    if not request.user.is_authenticated:
        return redirect('login')

    course = Course.objects.get(id=course_id)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    amount = int(course.price * 100)  # convert to paise

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    # ✅ Save payment
    payment = Payment.objects.create(
        user=request.user,
        course_name=course.title,
        amount=amount,
        order_id=order['id'],
        status="created"
    )

    context = {
        "order_id": order['id'],
        "amount": amount,
        "display_amount": course.price,
        "key": settings.RAZORPAY_KEY_ID,
        "course": course
    }

    return render(request, "payments/payment.html", context)


# ✅ VERIFY PAYMENT
@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)

        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")

        try:
            payment = Payment.objects.get(order_id=order_id)

            # ✅ Update payment details
            payment.payment_id = payment_id
            payment.status = "success"
            payment.save()

            # ✅ Get course
            course = Course.objects.get(title=payment.course_name)

            # ✅ Create Enrollment (Avoid duplicate)
            if not Enrollment.objects.filter(user=payment.user, course=course).exists():
                Enrollment.objects.create(
                    user=payment.user,
                    name=payment.user.username,  # auto-fill
                    phone="0000000000",  # temporary (you can improve later)
                    course=course,
                    is_verified=True  # since payment success
                )

            return HttpResponse("OK")

        except Exception as e:
            print("Payment Error:", e)
            return HttpResponse("FAIL")
from django.shortcuts import render

def payment_success(request):
    return render(request, 'payments/success.html')

def payment_failure(request):
    course_id = request.GET.get('course_id')
    return render(request, 'payments/failure.html', {'course_id': course_id})     


@login_required
def payment_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/payment_history.html', {'payments': payments})

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json

@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body)

        event = data.get("event")

        if event == "payment.captured":
            payment_data = data["payload"]["payment"]["entity"]
            payment_id = payment_data["id"]

            print("Payment Success:", payment_id)

        return HttpResponse(status=200)