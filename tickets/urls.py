from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminTicketViewSet, AdminTechnicianViewSet,
    QuotationViewSet, AdditionalProductViewSet,
    TechnicianNotificationViewSet, OutwardProductAssignmentViewSet,
    admin_summary
)

router = DefaultRouter()
router.register(r'admin/tickets', AdminTicketViewSet, basename='admin-ticket')
router.register(r'admin/technicians', AdminTechnicianViewSet, basename='admin-technician')
router.register(r'quotations', QuotationViewSet, basename='quotation')
router.register(r'additional-products', AdditionalProductViewSet, basename='additional-product')
router.register(r'technician/notifications', TechnicianNotificationViewSet, basename='technician-notification')
router.register(r'outward-products', OutwardProductAssignmentViewSet, basename='outward-product')

urlpatterns = [
    path('api/admin/summary/', admin_summary, name='admin-summary'),
    path('api/', include(router.urls)),
] 