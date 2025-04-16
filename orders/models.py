from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50, default="Pending")  # Status: Pending, Paid, Refunded

    def __str__(self):
        return f"Order {self.id} - {self.product.name}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=50)
    payment_request_payload = models.TextField()
    payment_response_payload = models.TextField()

    def __str__(self):
        return f"Payment for Order {self.order.id}"
    
