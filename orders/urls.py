from django.urls import path
from . import views

urlpatterns = [
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),
    path('', views.home_page, name='create_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('success/<int:payment_id>/', views.success, name='success'),
    path('failure/<int:payment_id>/', views.failure, name='failure'),
    path('create_order/', views.create_order, name='create_order')
]
