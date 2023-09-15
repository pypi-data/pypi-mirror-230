from django.conf import settings
from django.urls import path, include
from rest_framework import routers

from . import views
from .views.cloudpayments import CloudpaymentView


app_name = 'garpix_order'


router = routers.DefaultRouter()
router.register(r'robokassa', views.RobokassaView, basename='robokassa')

urlpatterns = [
    path('cloudpayments/pay/', CloudpaymentView.pay_view),
    path('cloudpayments/fail/', CloudpaymentView.fail_view),
    path('cloudpayments/payment_data/', CloudpaymentView.payment_data_view),
    path(f'{settings.API_URL}/', include(router.urls))
]
