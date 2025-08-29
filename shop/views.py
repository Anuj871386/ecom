from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


@api_view(['POST'])
def add_product(request):
    serializer = ProductSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save()
    return Response(ProductSerializer(product).data)


@api_view(['POST'])
def place_order(request):
    # Expecting: {"product_id": 1, "quantity": 2}
    product_id = request.data.get('product_id')
    qty = int(request.data.get('quantity', 0))
    if qty <= 0:
        return Response({'error': 'Quantity must be > 0'}, status=400)


    try:
        with transaction.atomic():
            # select_for_update to lock row and prevent oversell
            product = Product.objects.select_for_update().get(id=product_id)
            if product.stock_qty < qty:
                return Response({'error': 'Insufficient stock'}, status=400)
            product.stock_qty -= qty
            product.save()
            order = Order.objects.create(product=product, quantity=qty, total_price=product.price * qty)
            return Response({'order_id': order.id, 'total_price': float(order.total_price)})
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)


@api_view(['GET'])
def top_products(request):
    # Aggregation: total quantity sold per product, order by total sold desc
    data = (
    Order.objects.values('product__id', 'product__name')
    .annotate(total_sold=Sum('quantity'))
    .order_by('-total_sold')[:10]
    )
    return Response(list(data))


@api_view(['GET'])
def revenue_per_product(request):
    # SQL-like aggregation: sum total_price per product
    data = (
    Order.objects.values('product__id', 'product__name')
    .annotate(revenue=Sum('total_price'))
    .order_by('-revenue')
    )
    # Return as list of dicts
    return Response([{'product_id': d['product__id'], 'name': d['product__name'], 'revenue': float(d['revenue'] or 0)} for d in data])


# Frontend page
from django.template import loader


def top_products_page(request):
    data = (
    Order.objects.values('product__name')
    .annotate(total_sold=Sum('quantity'))
    .order_by('-total_sold')[:10]
    )
    return render(request, 'shop/top_products.html', {'products': data})    
