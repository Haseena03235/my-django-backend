from rest_framework import serializers
from .models import Ticket, Quotation, QuotationItem, AdditionalProduct, TicketStatusHistory, Notification, OutwardProductAssignment
from django.contrib.auth.models import User
from products.models import Product

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class QuotationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationItem
        fields = ['id', 'description', 'price', 'quantity']

class QuotationSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = ['id', 'created_at', 'accepted_by_customer', 'accepted_at', 'notes', 'items', 'total']
    
    def get_total(self, obj):
        return obj.total_amount

class AdditionalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalProduct
        fields = ['id', 'name', 'description', 'price', 'quantity', 'sold_at']

class TicketStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketStatusHistory
        fields = ['id', 'status', 'changed_by', 'changed_at', 'notes']

class TicketSerializer(serializers.ModelSerializer):
    assigned_technician = UserSerializer(read_only=True)
    quotation = QuotationSerializer(read_only=True)
    additional_products = AdditionalProductSerializer(many=True, read_only=True)
    status_history = TicketStatusHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'customer_name', 'customer_mobile', 'customer_email', 'address',
            'service_type', 'description', 'date_raised', 'date_attending',
            'status', 'assigned_technician', 'quotation', 'amount_paid',
            'notes', 'created_at', 'updated_at', 'additional_products', 'status_history'
        ]

class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'customer_name', 'customer_mobile', 'customer_email', 'address',
            'service_type', 'description', 'date_attending'
        ]

class TicketUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'status', 'assigned_technician', 'amount_paid', 'notes', 'date_attending'
        ]

class QuotationCreateSerializer(serializers.ModelSerializer):
    items = QuotationItemSerializer(many=True)
    
    class Meta:
        model = Quotation
        fields = ['ticket', 'notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        quotation = Quotation.objects.create(**validated_data)
        
        for item_data in items_data:
            QuotationItem.objects.create(quotation=quotation, **item_data)
        
        return quotation

class QuotationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = ['accepted_by_customer', 'accepted_at', 'notes']

class AdditionalProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalProduct
        fields = ['ticket', 'name', 'description', 'price', 'quantity']

class TicketListSerializer(serializers.ModelSerializer):
    assigned_technician_name = serializers.SerializerMethodField()
    quotation_total = serializers.SerializerMethodField()
    quotation_accepted = serializers.SerializerMethodField()
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'customer_name', 'customer_mobile', 'service_type', 'description',
            'date_raised', 'status', 'assigned_technician_name', 'quotation_total',
            'quotation_accepted', 'amount_paid'
        ]
    
    def get_assigned_technician_name(self, obj):
        if obj.assigned_technician:
            return f"{obj.assigned_technician.first_name} {obj.assigned_technician.last_name}"
        return None
    
    def get_quotation_total(self, obj):
        if obj.quotation:
            return obj.quotation.total_amount
        return None
    
    def get_quotation_accepted(self, obj):
        if obj.quotation:
            return obj.quotation.accepted_by_customer
        return None

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'title', 'message', 'created_at', 'read', 'related_ticket']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'image']

class OutwardProductAssignmentSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    technician = UserSerializer(read_only=True)
    pending_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = OutwardProductAssignment
        fields = ['id', 'technician', 'product', 'quantity_assigned', 'quantity_returned', 'assigned_at', 'returned_at', 'status', 'pending_quantity'] 