from django.contrib import admin
from .models import Ticket, Quotation, QuotationItem, AdditionalProduct, TicketStatusHistory, Notification

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_mobile', 'service_type', 'status', 'assigned_technician', 'date_raised']
    list_filter = ['status', 'service_type', 'date_raised', 'assigned_technician']
    search_fields = ['customer_name', 'customer_mobile', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date_raised'
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer_name', 'customer_mobile', 'customer_email', 'address')
        }),
        ('Ticket Details', {
            'fields': ('service_type', 'description', 'date_raised', 'date_attending')
        }),
        ('Status and Assignment', {
            'fields': ('status', 'assigned_technician')
        }),
        ('Financial', {
            'fields': ('quotation', 'amount_paid')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'total_amount', 'accepted_by_customer', 'created_at']
    list_filter = ['accepted_by_customer', 'created_at']
    search_fields = ['ticket__customer_name', 'notes']
    readonly_fields = ['created_at']

@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'quotation', 'description', 'price', 'quantity']
    list_filter = ['quotation__ticket__service_type']
    search_fields = ['description']

@admin.register(AdditionalProduct)
class AdditionalProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'name', 'price', 'quantity', 'sold_at']
    list_filter = ['sold_at']
    search_fields = ['name', 'description', 'ticket__customer_name']
    readonly_fields = ['sold_at']

@admin.register(TicketStatusHistory)
class TicketStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'status', 'changed_by', 'changed_at']
    list_filter = ['status', 'changed_at']
    search_fields = ['ticket__customer_name', 'notes']
    readonly_fields = ['changed_at']
    date_hierarchy = 'changed_at'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'title', 'created_at', 'read', 'related_ticket']
    list_filter = ['read', 'created_at', 'recipient']
    search_fields = ['title', 'message', 'recipient__username']
    readonly_fields = ['created_at']
