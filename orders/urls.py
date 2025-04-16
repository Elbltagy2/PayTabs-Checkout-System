from django.urls import path
from . import views

urlpatterns = [
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),
    path('', views.create_order, name='create_order'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('success/<int:order_number>/', views.success, name='success'),
    path('failure/<int:order_number>/', views.failure, name='failure'),
]
