from django.urls import path
from . import views

urlpatterns = [
    # path('pay/', views.create_payment, name='pay'),
    # path('verify/', views.verify_payment, name='verify_payment'),

    path('pay/<int:course_id>/', views.create_payment, name='pay'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('failure/', views.payment_failure, name='payment_failure'),
    path('webhook/', views.razorpay_webhook),
    path('history/', views.payment_history, name='payment_history'),

]