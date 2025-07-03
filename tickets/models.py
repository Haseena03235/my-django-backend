from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from products.models import Product

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('completed', 'Completed'),
    ]
    
    SERVICE_TYPE_CHOICES = [
        ('ac_repair', 'AC Repair'),
        ('ac_service', 'AC Service'),
        ('refrigerator_repair', 'Refrigerator Repair'),
        ('washing_machine_repair', 'Washing Machine Repair'),
        ('tv_repair', 'TV Repair'),
        ('microwave_repair', 'Microwave Repair'),
        ('other', 'Other'),
    ]
    
    # Customer Information
    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    customer_email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    # Ticket Details
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)
    description = models.TextField()
    date_raised = models.DateTimeField(auto_now_add=True)
    date_attending = models.DateTimeField(blank=True, null=True)
    
    # Status and Assignment
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_technician = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_tickets',
        limit_choices_to={'groups__name': 'Technicians'}
    )
    
    # Quotation and Payment
    quotation = models.OneToOneField('Quotation', on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_ref')
    amount_paid = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.customer_name} - {self.service_type}"
    
    @property
    def total_amount(self):
        """Calculate total amount including quotation and additional products"""
        total = self.amount_paid
        if self.quotation:
            total += self.quotation.total_amount
        return total

class Quotation(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='ticket_quotation')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_by_customer = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Quotation for Ticket #{self.ticket.id}"
    
    @property
    def total_amount(self):
        """Calculate total amount from all items"""
        return sum(item.price for item in self.items.all())

class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.description} - ₹{self.price}"

class AdditionalProduct(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='additional_products')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    quantity = models.PositiveIntegerField(default=1)
    sold_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - ₹{self.price}"

class TicketStatusHistory(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Ticket.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Ticket Status History'
    
    def __str__(self):
        return f"Ticket #{self.ticket.id} - {self.status} at {self.changed_at}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    related_ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title} ({'Read' if self.read else 'Unread'})"

class OutwardProductAssignment(models.Model):
    technician = models.ForeignKey(User, on_delete=models.CASCADE, related_name='outward_assignments')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_assigned = models.PositiveIntegerField()
    quantity_returned = models.PositiveIntegerField(default=0)
    assigned_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('returned', 'Returned')], default='pending')

    @property
    def pending_quantity(self):
        return self.quantity_assigned - self.quantity_returned

    def __str__(self):
        return f"{self.technician.username} - {self.product.name} ({self.quantity_assigned} assigned, {self.quantity_returned} returned)"
