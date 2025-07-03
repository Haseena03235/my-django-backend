from django.urls import path
from .views import create_technician, admin_transactions

urlpatterns = [
    path('api/admin/technicians/create/', create_technician, name='create-technician'),
    path('admin/transactions/', admin_transactions, name='admin_transactions'),
] 