"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import admin_profile
from rest_framework import routers
from django.http import HttpResponse
from rest_framework.authtoken.views import obtain_auth_token

# Import your ViewSets from their respective apps
from products.views import ProductViewSet
from orders.views import OrderViewSet
from tickets.views import TicketViewSet
from users.views import UserViewSet

# Create the router and register your ViewSets
router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'users', UserViewSet)
# Add more as needed

def home(request):
    return HttpResponse("Welcome to your Django backend!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    # path('api/', include('products.urls')),
    # path('api/', include('tickets.urls')),
    # path('api/', include('users.urls')),
    path('api/admin/profile/', admin_profile, name='admin_profile'),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('', home),
]
