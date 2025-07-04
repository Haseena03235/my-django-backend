from django.urls import path
from .views import create_technician, admin_transactions, forgot_password

urlpatterns = [
    path('admin/technicians/create/', create_technician, name='create-technician'),
    path('admin/transactions/', admin_transactions, name='admin_transactions'),
    path('forgot-password/', forgot_password, name='forgot-password'),
] 