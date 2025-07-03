from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from users.models import TechnicianProfile
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
import random
import string
from django.http import JsonResponse

# Create your views here.

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def admin_profile(request):
    if request.method == 'GET':
        return Response({
            'username': request.user.username,
            'email': request.user.email,
        })
    elif request.method == 'PUT':
        data = request.data
        user = request.user
        
        # Update username and email
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        
        # Update password if provided
        if 'new_password' in data and data['new_password']:
            if user.check_password(data.get('current_password', '')):
                user.set_password(data['new_password'])
            else:
                return Response({'error': 'Current password is incorrect'}, status=400)
        
        user.save()
        return Response({'message': 'Profile updated successfully'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_technician(request):
    data = request.data
    name = data.get('name')
    email = data.get('email')
    mobile = data.get('mobile')
    dob = data.get('dob')
    gender = data.get('gender')
    address = data.get('address')
    profile_photo = request.FILES.get('profile_photo')

    # Generate random password
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # Create user
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name=name.split()[0],
        last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
    )
    # Assign to Technicians group
    group, _ = Group.objects.get_or_create(name='Technicians')
    user.groups.add(group)

    # Create profile
    TechnicianProfile.objects.create(
        user=user,
        mobile=mobile,
        dob=dob,
        gender=gender,
        address=address,
        profile_photo=profile_photo
    )

    # Send email
    send_mail(
        subject='Your Technician Account',
        message=f'Hello {name},\n\nYour technician account has been created.\nEmail: {email}\nPassword: {password}\n\nPlease log in and change your password.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({'status': 'success', 'message': 'Technician created and email sent.'})

@api_view(['GET'])
def admin_transactions(request):
    # Example: return a dummy list of transactions
    data = [
        {"id": 1, "amount": 100, "status": "completed"},
        {"id": 2, "amount": 200, "status": "pending"},
    ]
    return Response(data)
