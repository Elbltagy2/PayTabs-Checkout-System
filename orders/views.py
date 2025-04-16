from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Product, Payment
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
# View to show all orders

PAYTABS_API_URL = 'https://secure-egypt.paytabs.com/payment/request'
PAYTABS_API_KEY = 'SWJ992BZTN-JHGTJBWDLM-BZJKMR2ZHT'

@csrf_exempt  # Disable CSRF protection for this view (for testing purposes)
def my_orders(request):
    orders = Order.objects.all()
    return render(request, 'orders/my_orders.html', {'orders': orders})

def success(request,order_number):
    # Get the order number from the URL
    return render(request, 'orders/success.html', {'order_number': order_number})
def failure(request,order_number):
    return render(request, 'orders/failure.html',{'order_number': order_number})

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
    return render(request, 'orders/home_page.html', {'products': products})

# Checkout view

def checkout(request):
    return render(request, 'orders/checkout.html')

@csrf_exempt  # Disable CSRF protection for this view (for testing purposes)
def process_payment(request):
    order_number='1'
    if request.method == 'POST':
        try:
            # Define the constant payment data (for testing)
            payment_data = {
                "profile_id": "132344",
                "tran_type": "sale",
                "tran_class": "ecom",
                "cart_id": "cart_11111",  # Example cart ID
                "cart_currency": "EGP",
                "cart_amount": 12.3,  # Total amount
                "cart_description": "Description of the items/services",
                "paypage_lang": "en",
                "customer_details": {
                    "name": "Your Full Name",
                    "email": "your-email@domain.com",
                    "phone": "Your Phone Number",
                    "country": "EG",
                    "state": "Cairo",
                    "city": "Cairo",
                    "street1": "address street",
                    "zip": "12345"
                },
                "shipping_details": {
                    "name": "Your Full Name",
                    "email": "your-email@domain.com",
                    "phone": "Your Phone Number",
                    "country": "EG",
                    "state": "Cairo",
                    "city": "Cairo",
                    "street1": "shipping address",
                    "zip": "54321"
                },
                "callback": "http://127.0.0.1:8080/failure/1",
                "framed": True,
                "framed_return_top": True,
                "framed_return_parent": True,
                "return": "http://127.0.0.1:8080/success/1",
            }

         
            # Set the headers for the PayTabs API request
            headers = {
                'Authorization': 'SWJ992BZTN-JHGTJBWDLM-BZJKMR2ZHT',
                'Content-Type': 'application/json',
            }

            # Make the POST request to PayTabs API
            response = requests.post(PAYTABS_API_URL, headers=headers, json=payment_data)

            # Handle PayTabs response
            if response.status_code == 200:
                paytabs_response = response.json()
                # Log the response from PayTabs
                print("PayTabs Response:", paytabs_response)

                # Return the response back to the frontend (with the payment URL or error)
                return JsonResponse(paytabs_response)

            else:
                # Return an error message if PayTabs responds with an error
                return JsonResponse({'error': 'Error processing payment with PayTabs', 'details': response.text}, status=500)

        except Exception as e:
            # Return a general error message if something goes wrong
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Return an error message if the request is not POST
        return JsonResponse({'error': 'Invalid request method'}, status=400)