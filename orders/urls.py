from django.urls import path
from . import views

urlpatterns = [
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_details/<int:order_id>/', views.order_details, name='order_details'),
    path('create_order/', views.create_order, name='create_order'),
    path('checkout/<int:order_id>/', views.checkout, name='checkout'),
]
