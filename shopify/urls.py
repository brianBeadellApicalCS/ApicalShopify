from django.urls import path
from . import views

app_name = 'shopify'

urlpatterns = [
    path('', views.home, name='home'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/error/', views.payment_error, name='payment_error'),
    path('webhook/', views.webhook, name='webhook'),
    path('download-labels/<int:order_id>/', views.download_labels, name='download_labels'),
    path('print-labels/<int:order_id>/', views.print_labels, name='print_labels'),
    path('preview-pdf/<int:order_id>/', views.preview_pdf, name='preview_pdf'),
    path('email-pdf/<int:order_id>/', views.email_pdf, name='email_pdf'),
    path('batch-download/', views.batch_download, name='batch_download'),
]
