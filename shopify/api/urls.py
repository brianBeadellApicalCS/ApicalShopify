from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:pk>/generate-pdf/', 
         views.OrderPDFGeneration.as_view(), 
         name='order-pdf-generate'),
    path('batch/generate-pdfs/', 
         views.BatchPDFGeneration.as_view(), 
         name='batch-pdf-generate'),
] 