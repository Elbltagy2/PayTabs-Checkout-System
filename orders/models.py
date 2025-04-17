from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class Order(models.Model):
    status = models.CharField(max_length=50, default="Pending")  # Status: Pending, Paid, Refunded
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # New field to store total price

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)  # Link to the order
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Link to the product
    quantity = models.PositiveIntegerField()  # Quantity of the product ordered
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product at the time of the order

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs"

    def total_price(self):
        return self.price * self.quantity


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=50)  # e.g., 'Completed', 'Failed'
    payment_request_payload = models.TextField()  # JSON or raw request data sent to payment provider
    payment_response_payload = models.TextField()  # Response data received from payment provider

    def __str__(self):
        return f"Payment for Order {self.order.id}"
