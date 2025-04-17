from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Product, Payment,OrderItem
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

def success(request, payment_id):
    try:
        # Step 1: Get the Payment record using the payment_id
        payment = get_object_or_404(Payment, id=payment_id)

        # Step 2: Update the Payment status to "Success"
        payment.payment_status = 'Success'
        payment.save()

        # Step 3: Update the related Order status to "Paid"
        order = payment.order  # The related order is accessible through the Payment model
        order.status = 'Paid'
        order.save()

        # Step 4: Render the success page and pass the payment_id
        return render(request, 'orders/success.html', {'payment_id': payment_id})

    except Exception as e:
        # Handle any errors that occur (e.g., payment_id not found, etc.)
        return JsonResponse({'error': str(e)}, status=400)

def failure(request,order_number):
    return render(request, 'orders/failure.html',{'order_number': order_number})

# View to show order details
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = Payment.objects.filter(order=order).first()
    return render(request, 'orders/order_details.html', {'order': order, 'payment': payment})

# View to create new order
def home_page(request):
    products = Product.objects.all()
    return render(request, 'orders/home_page.html', {'products': products})

@csrf_exempt  # Disable CSRF protection for this view (for testing purposes)
def create_order(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data (cart data)
            data = json.loads(request.body)
            cart_data = data.get('cart_data', [])  # Cart items (list of products and quantities)

            if not cart_data:
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            # Create the order (initial status: Pending)
            order = Order.objects.create(status='Pending', total_price=0)

            total_price = 0
            # Create OrderItems for each product in the cart
            for item in cart_data:
                try:
                    product = Product.objects.get(id=item['id'])  # Fetch product from DB
                    item_price = product.price * item['quantity']  # Calculate price for this item
                    
                    # Create an OrderItem instance for the product
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item['quantity'],
                        price=product.price
                    )
                    total_price += item_price  # Add to total price of the order
                except Product.DoesNotExist:
                    return JsonResponse({'error': f'Product {item["id"]} not found'}, status=400)

            # Update the total price for the order
            order.total_price = total_price
            order.save()

            # Return the created order id and total price
            return JsonResponse({'order_id': order.id, 'total_price': total_price})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def checkout(request):
    return render(request, 'orders/checkout.html')

@csrf_exempt  # Disable CSRF protection for this view (for testing purposes)
def process_payment(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        order_id = body.get('order_id')
        try:
            # Step 1: Prepare payment data
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
                    "name": "Ahmedelbltagy",
                    "email": "ahmedelbltagy125@gmail.com",
                    "phone": "Your Phone Number",
                    "country": "EG",
                    "state": "Cairo",
                    "city": "Cairo",
                    "street1": "address street",
                    "zip": "12345"
                },
                "shipping_details": {
                    "name": "Ahmedelbltagy",
                    "email": "ahmedelbltagy125@gmail.com",
                    "phone": "Your Phone Number",
                    "country": "EG",
                    "state": "Cairo",
                    "city": "Cairo",
                    "street1": "shipping address",
                    "zip": "54321"
                },
                # Include the payment ID in the callback URL
                "callback": f"http://127.0.0.1:8080/failure/{{payment_id}}",  # Placeholder for payment_id
                "framed": True,
                "framed_return_top": True,
                "framed_return_parent": True,
                "return": "http://127.0.0.1:8080/success/{{payment.id}}",
            }
          
            # Step 2: Create the Payment record in the database (initially with status 'Pending')
            payment = Payment.objects.create(
                order=Order.objects.get(id=order_id),  # Link to the order
                payment_status='Pending',  # Initially set status as 'Pending'
                payment_request_payload=json.dumps(payment_data)  # Save the payment request
            )

            # Step 3: Update the callback URL with the real payment ID
            payment_data['callback'] = f"http://127.0.0.1:8080/failure/{payment.id}"
            payment_data['return']= f"http://127.0.0.1:8080/success/{payment.id}"

            # Set the headers for the PayTabs API request
            headers = {
                'Authorization': 'SWJ992BZTN-JHGTJBWDLM-BZJKMR2ZHT',
                'Content-Type': 'application/json',
            }
            # Step 4: Send the payment request to PayTabs API
            response = requests.post(PAYTABS_API_URL, headers=headers, json=payment_data)

            # Handle PayTabs response
            if response.status_code == 200:
                paytabs_response = response.json()
                # Save the PayTabs response payload in the Payment record
                payment.payment_response_payload = json.dumps(paytabs_response)
                payment.save()  # Save the response in the database

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