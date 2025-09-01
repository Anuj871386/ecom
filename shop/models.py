from django.db import models
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock_qty = models.IntegerField()


def __str__(self):
    return self.name


class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders', db_index=True)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=14, decimal_places=2)
    order_date = models.DateTimeField(default=timezone.now)


def __str__(self):
    return f"Order #{self.id}"
