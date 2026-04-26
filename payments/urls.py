from django.urls import path
from . import views

urlpatterns = [
    #Payment Flow
    path('pay/<int:course_id>/', views.create_payment, name='pay'),
    path('verify/', views.verify_payment, name='verify_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('failure/', views.payment_failure, name='payment_failure'),

    # User Features
    path('history/', views.payment_history, name='payment_history'),
    path('invoice/<int:payment_id>/', views.download_invoice, name='download_invoice'),
    path('dashboard/', views.payment_dashboard, name='payment_dashboard'),
    path('dashboard-data/', views.dashboard_data),

    # Charts
    path('chart/', views.revenue_chart, name='revenue_chart'),
    path('pie-chart/', views.payment_pie_chart, name='pie_chart'),
    path('daily-chart/', views.daily_revenue, name='daily_chart'),

    #  Export
    path('export/', views.export_excel, name='export_excel'),

    # Webhook
    path('webhook/', views.razorpay_webhook, name='webhook'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]