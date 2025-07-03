from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.db.models import Q, Sum
from django.http import HttpResponse
from .models import Ticket, Quotation, QuotationItem, AdditionalProduct, TicketStatusHistory, Notification, OutwardProductAssignment, Product
from .serializers import (
    TicketSerializer, TicketCreateSerializer, TicketUpdateSerializer, TicketListSerializer,
    QuotationSerializer, QuotationCreateSerializer, QuotationUpdateSerializer,
    AdditionalProductSerializer, AdditionalProductCreateSerializer,
    TicketStatusHistorySerializer, UserSerializer, NotificationSerializer,
    OutwardProductAssignmentSerializer, ProductSerializer
)
from .utils import generate_quotation_pdf, save_quotation_pdf
import json

class AdminTicketViewSet(viewsets.ModelViewSet):
    """
    Admin API for managing tickets
    """
    queryset = Ticket.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TicketUpdateSerializer
        elif self.action == 'list':
            return TicketListSerializer
        return TicketSerializer
    
    def get_queryset(self):
        queryset = Ticket.objects.select_related(
            'assigned_technician', 'quotation'
        ).prefetch_related(
            'quotation__items', 'additional_products', 'status_history'
        )
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(customer_name__icontains=search) |
                Q(service_type__icontains=search) |
                Q(description__icontains=search) |
                Q(id__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_update(self, serializer):
        ticket = serializer.save()
        
        # Record status change in history
        if 'status' in serializer.validated_data:
            TicketStatusHistory.objects.create(
                ticket=ticket,
                status=serializer.validated_data['status'],
                changed_by=self.request.user,
                notes=f"Status changed to {serializer.validated_data['status']}"
            )
    
    @action(detail=True, methods=['post'])
    def accept_ticket(self, request, pk=None):
        """Accept a pending ticket"""
        ticket = self.get_object()
        if ticket.status != 'pending':
            return Response(
                {'error': 'Only pending tickets can be accepted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = 'accepted'
        ticket.save()
        
        TicketStatusHistory.objects.create(
            ticket=ticket,
            status='accepted',
            changed_by=request.user,
            notes='Ticket accepted by admin'
        )
        
        return Response({'message': 'Ticket accepted successfully'})
    
    @action(detail=True, methods=['post'])
    def reject_ticket(self, request, pk=None):
        """Reject a pending ticket"""
        ticket = self.get_object()
        if ticket.status != 'pending':
            return Response(
                {'error': 'Only pending tickets can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ticket.status = 'rejected'
        ticket.save()
        
        TicketStatusHistory.objects.create(
            ticket=ticket,
            status='rejected',
            changed_by=request.user,
            notes='Ticket rejected by admin'
        )
        
        return Response({'message': 'Ticket rejected successfully'})
    
    @action(detail=True, methods=['post'])
    def assign_technician(self, request, pk=None):
        """Assign a technician to a ticket and notify the technician"""
        ticket = self.get_object()
        technician_id = request.data.get('technician_id')
        if not technician_id:
            return Response({'error': 'Technician ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            technician = User.objects.get(id=technician_id)
            if not technician.groups.filter(name='Technicians').exists():
                return Response({'error': 'User is not a technician'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'error': 'Technician not found'}, status=status.HTTP_404_NOT_FOUND)
        ticket.assigned_technician = technician
        ticket.status = 'in_progress'
        ticket.save()
        TicketStatusHistory.objects.create(
            ticket=ticket,
            status='in_progress',
            changed_by=request.user,
            notes=f'Assigned to technician: {technician.get_full_name()}'
        )
        # Create notification for technician
        Notification.objects.create(
            recipient=technician,
            title='New Ticket Assigned',
            message=f'You have been assigned ticket #{ticket.id}.',
            related_ticket=ticket
        )
        return Response({'message': 'Technician assigned successfully'})
    
    @action(detail=True, methods=['post'])
    def create_quotation(self, request, pk=None):
        """Create a quotation for a ticket"""
        ticket = self.get_object()
        
        if ticket.quotation:
            return Response(
                {'error': 'Quotation already exists for this ticket'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = QuotationCreateSerializer(data=request.data)
        if serializer.is_valid():
            quotation = serializer.save()
            return Response(
                QuotationSerializer(quotation).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_additional_product(self, request, pk=None):
        """Add additional product to a ticket"""
        ticket = self.get_object()
        
        serializer = AdditionalProductCreateSerializer(data=request.data)
        if serializer.is_valid():
            additional_product = serializer.save()
            return Response(
                AdditionalProductSerializer(additional_product).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """Mark ticket as resolved"""
        ticket = self.get_object()
        ticket.status = 'resolved'
        ticket.save()
        
        TicketStatusHistory.objects.create(
            ticket=ticket,
            status='resolved',
            changed_by=request.user,
            notes='Ticket marked as resolved'
        )
        
        return Response({'message': 'Ticket marked as resolved'})
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark ticket as completed"""
        ticket = self.get_object()
        ticket.status = 'completed'
        ticket.save()
        
        TicketStatusHistory.objects.create(
            ticket=ticket,
            status='completed',
            changed_by=request.user,
            notes='Ticket marked as completed'
        )
        
        return Response({'message': 'Ticket marked as completed'})
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """Generate PDF for ticket quotation"""
        ticket = self.get_object()
        
        if not ticket.quotation:
            return Response(
                {'error': 'No quotation found for this ticket'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate PDF
            buffer = generate_quotation_pdf(ticket, ticket.quotation)
            
            # Create response
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="quotation_ticket_{ticket.id}.pdf"'
            
            return response
        except Exception as e:
            return Response(
                {'error': f'PDF generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AdminTechnicianViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin API for viewing technicians
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Get users in the Technicians group
        try:
            technician_group = Group.objects.get(name='Technicians')
            return User.objects.filter(groups=technician_group)
        except Group.DoesNotExist:
            return User.objects.none()

class QuotationViewSet(viewsets.ModelViewSet):
    """
    API for managing quotations
    """
    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return QuotationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return QuotationUpdateSerializer
        return QuotationSerializer
    
    @action(detail=True, methods=['post'])
    def accept_quotation(self, request, pk=None):
        """Customer accepts a quotation"""
        quotation = self.get_object()
        quotation.accepted_by_customer = True
        quotation.accepted_at = timezone.now()
        quotation.save()
        
        return Response({'message': 'Quotation accepted successfully'})
    
    @action(detail=True, methods=['post'])
    def reject_quotation(self, request, pk=None):
        """Customer rejects a quotation"""
        quotation = self.get_object()
        quotation.accepted_by_customer = False
        quotation.save()
        
        return Response({'message': 'Quotation rejected successfully'})

class AdditionalProductViewSet(viewsets.ModelViewSet):
    """
    API for managing additional products
    """
    queryset = AdditionalProduct.objects.all()
    serializer_class = AdditionalProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AdditionalProductCreateSerializer
        return AdditionalProductSerializer

class TechnicianNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

class OutwardProductAssignmentViewSet(viewsets.ModelViewSet):
    queryset = OutwardProductAssignment.objects.all()
    serializer_class = OutwardProductAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Technicians').exists():
            return OutwardProductAssignment.objects.filter(technician=user)
        return OutwardProductAssignment.objects.all()

    @action(detail=True, methods=['post'])
    def mark_returned(self, request, pk=None):
        assignment = self.get_object()
        qty = int(request.data.get('quantity', 0))
        if qty > 0 and assignment.pending_quantity >= qty:
            assignment.quantity_returned += qty
            if assignment.quantity_returned == assignment.quantity_assigned:
                assignment.status = 'returned'
                assignment.returned_at = timezone.now()
            assignment.save()
            return Response({'status': 'success', 'pending': assignment.pending_quantity})
        return Response({'status': 'error', 'message': 'Invalid quantity'}, status=400)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_summary(request):
    from tickets.models import Ticket, Product, Notification
    from products.models import Category
    from django.contrib.auth.models import User, Group
    # Products & Categories
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    # Customers & Technicians
    total_customers = User.objects.filter(groups__name='Customers').count()
    total_technicians = User.objects.filter(groups__name='Technicians').count()
    # Orders (assuming AdditionalProduct is an order, adjust as needed)
    from tickets.models import AdditionalProduct
    total_pending_orders = AdditionalProduct.objects.filter(ticket__status='pending').count()
    total_completed_orders = AdditionalProduct.objects.filter(ticket__status='completed').count()
    total_cancelled_orders = AdditionalProduct.objects.filter(ticket__status='cancelled').count() if 'cancelled' in [c[0] for c in Ticket.STATUS_CHOICES] else 0
    # Tickets
    total_pending_tickets = Ticket.objects.filter(status='pending').count()
    total_completed_tickets = Ticket.objects.filter(status='completed').count()
    # Feedback (assuming Notification is feedback, adjust as needed)
    total_feedback = Notification.objects.count()
    # Amounts (adjust as needed)
    total_sales_amount = AdditionalProduct.objects.aggregate(total=Sum('price'))['total'] or 0
    total_services_amount = Ticket.objects.aggregate(total=Sum('amount_paid'))['total'] or 0
    total_visit_charges = Ticket.objects.aggregate(total=Sum('quotation__items__price'))['total'] or 0
    return Response({
        'total_products': total_products,
        'total_categories': total_categories,
        'total_customers': total_customers,
        'total_technicians': total_technicians,
        'total_pending_orders': total_pending_orders,
        'total_completed_orders': total_completed_orders,
        'total_cancelled_orders': total_cancelled_orders,
        'total_pending_tickets': total_pending_tickets,
        'total_completed_tickets': total_completed_tickets,
        'total_feedback': total_feedback,
        'total_sales_amount': total_sales_amount,
        'total_services_amount': total_services_amount,
        'total_visit_charges': total_visit_charges,
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def admin_transactions(request):
    transactions = []
    for payment in Payment.objects.select_related('order').all().order_by('-date'):
        order = payment.order
        for item in order.items.all():
            transactions.append({
                'date': payment.date.strftime('%Y-%m-%d'),
                'order_id': order.id,
                'order_details': f'{order.customer_name}, {order.address}',
                'product_name': item.product.name,
                'description': item.product.description,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'total_price': float(item.unit_price) * item.quantity,
                'status': payment.status,  # e.g. 'Payment Authorized', 'Order Shipped', etc.
            })
    return Response(transactions)
