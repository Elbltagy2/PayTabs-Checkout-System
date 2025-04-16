from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Product, Payment
# View to show all orders
def my_orders(request):
    orders = Order.objects.all()
    return render(request, 'orders/my_orders.html', {'orders': orders})

# View to show order details
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = Payment.objects.filter(order=order).first()
    return render(request, 'orders/order_details.html', {'order': order, 'payment': payment})

# View to create new order
def create_order(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        quantity = request.POST['quantity']
        product = Product.objects.get(id=product_id)
        order = Order(product=product, quantity=quantity)
        order.save()
        return redirect('checkout', order_id=order.id)
    products = Product.objects.all()
    return render(request, 'orders/create_order.html', {'products': products})

# Checkout view

def checkout(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    print(f"Order ID: {order.id}, Product: {order.product.name}, Quantity: {order.quantity}")

    if request.method == 'POST':
        # Handle the PayTabs payment processing here
        # This is where you'll integrate the PayTabs iFrame.
        # For now, let's just display a success message.

        # Example logic: You could process the payment and update order status to 'Paid'
        order.status = 'Paid'  # Set order status to paid after payment (dummy for now)
        order.save()

        # You would normally handle PayTabs response here (success/error)
        return JsonResponse({'status': 'success', 'message': 'Payment processed successfully!'})

    return render(request, 'orders/checkout.html', {'order': order})
