from django.urls import path
from .views import CartView, CartAddItemView, CartUpdateItemView, CartRemoveItemView, CartClearView, CancelOrderView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', CartAddItemView.as_view(), name='cart-add'),
    path('cart/update/', CartUpdateItemView.as_view(), name='cart-update'),
    path('cart/remove/', CartRemoveItemView.as_view(), name='cart-remove'),
    path('cart/clear/', CartClearView.as_view(), name='cart-clear'),
    path('orders/<int:order_id>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
] 