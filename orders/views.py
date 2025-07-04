from django.shortcuts import render
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth.models import User
from .models import Cart, CartItem
from products.models import Product
from .serializers import CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404

# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        customer_id = request.query_params.get('customer_id')
        user = get_object_or_404(User, id=customer_id)
        cart, _ = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CartAddItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, id=request.data.get('customer_id'))
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        quantity = int(request.data.get('quantity', 1))
        cart, _ = Cart.objects.get_or_create(user=user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return Response({'message': 'Item added to cart.'}, status=status.HTTP_201_CREATED)

class CartUpdateItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, id=request.data.get('customer_id'))
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        quantity = int(request.data.get('quantity', 1))
        cart = get_object_or_404(Cart, user=user)
        item = get_object_or_404(CartItem, cart=cart, product=product)
        item.quantity = quantity
        item.save()
        return Response({'message': 'Cart item quantity updated.'})

class CartRemoveItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, id=request.data.get('customer_id'))
        product = get_object_or_404(Product, id=request.data.get('product_id'))
        cart = get_object_or_404(Cart, user=user)
        item = get_object_or_404(CartItem, cart=cart, product=product)
        item.delete()
        return Response({'message': 'Item removed from cart.'})

class CartClearView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = get_object_or_404(User, id=request.data.get('customer_id'))
        cart = get_object_or_404(Cart, user=user)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared.'})

class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status == 'delivered':
            return Response({'error': 'Order cannot be cancelled after delivery.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save()
        return Response({'message': 'Order cancelled successfully.'})
