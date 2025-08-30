from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from .forms import ProductForm, OrderForm


def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("add_product")   
    else:
        form = ProductForm()

    products = Product.objects.all()
    return render(request, "shop/products.html", {"form": form, "products": products})


def place_order(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            # calculate total price from product & qty
            order.total_price = order.product.price * order.quantity
            order.save()
            return redirect("place_order")
    else:
        form = OrderForm()

    orders = Order.objects.all()
    return render(request, "shop/orders.html", {"form": form, "orders": orders})


@api_view(['GET'])
def top_products(request):
    # Aggregation: total quantity sold per product, order by total sold desc
    data = (
    Order.objects.values('product__id', 'product__name')
    .annotate(total_sold=Sum('quantity'))
    .order_by('-total_sold')
    )
    print("anuj5------", data)
    return render(request, "shop/top_products.html", {"products": data})


@api_view(['GET'])
def revenue_per_product(request):
    # SQL-like aggregation: sum total_price per product
    data = (
    Order.objects.values('product__id', 'product__name')
    .annotate(revenue=Sum('total_price'))
    .order_by('-revenue')
    )
    print("anuj6----", data)
    # Return as list of dicts
    return render(request, "shop/revenue.html", {
    "products": [
        {
            "product_id": d["product__id"],
            "name": d["product__name"],
            "revenue": float(d["revenue"] or 0),
        }
        for d in data
    ]
})

# Frontend page
from django.template import loader


def top_products_page(request):
    data = (
    Order.objects.values('product__name')
    .annotate(total_sold=Sum('quantity'))
    .order_by('-total_sold')[:10]
    )
    print("anuj7----", data)
    return render(request, 'shop/top_10_products.html', {'products': data})    
