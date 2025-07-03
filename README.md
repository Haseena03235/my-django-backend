# Klevant Backend - Django API

This is the Django backend for the Klevant service management application.

## Features

### Ticket Management System
- **Complete Ticket Lifecycle**: From creation to completion
- **Admin Ticket Management**: View, accept/reject, assign technicians
- **Quotation Management**: Create and manage service quotations
- **PDF Generation**: Generate professional quotation PDFs
- **Status Tracking**: Track ticket status changes with history
- **Additional Products**: Sell additional products against tickets
- **Technician Assignment**: Assign technicians to accepted tickets

### User Management
- **Admin Profile Management**: Manage admin account details
- **User Management**: Manage customers, technicians, and staff
- **Technician Registration**: Register and manage technicians

### Product Management
- **Product CRUD**: Add, edit, delete products
- **Image Management**: Upload and manage product images
- **Category Management**: Organize products by categories

### Communication
- **Contact Messages**: Manage customer contact messages
- **Email Notifications**: Send real-time email notifications
- **Buyer Management**: Manage buyer information and profiles

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd klevant_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Create technician group**
   ```bash
   python manage.py shell
   ```
   ```python
   from django.contrib.auth.models import Group
   Group.objects.get_or_create(name='Technicians')
   exit()
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Ticket Management
- `GET /api/admin/tickets/` - List all tickets (admin)
- `GET /api/admin/tickets/{id}/` - Get ticket details
- `PATCH /api/admin/tickets/{id}/` - Update ticket
- `POST /api/admin/tickets/{id}/accept_ticket/` - Accept ticket
- `POST /api/admin/tickets/{id}/reject_ticket/` - Reject ticket
- `POST /api/admin/tickets/{id}/assign_technician/` - Assign technician
- `POST /api/admin/tickets/{id}/create_quotation/` - Create quotation
- `POST /api/admin/tickets/{id}/add_additional_product/` - Add product
- `POST /api/admin/tickets/{id}/mark_resolved/` - Mark as resolved
- `POST /api/admin/tickets/{id}/mark_completed/` - Mark as completed
- `GET /api/admin/tickets/{id}/generate_pdf/` - Generate PDF quotation

### Technician Management
- `GET /api/admin/technicians/` - List all technicians

### Quotation Management
- `GET /api/quotations/` - List quotations
- `POST /api/quotations/` - Create quotation
- `POST /api/quotations/{id}/accept_quotation/` - Accept quotation
- `POST /api/quotations/{id}/reject_quotation/` - Reject quotation

### Additional Products
- `GET /api/additional-products/` - List additional products
- `POST /api/additional-products/` - Add additional product

## Ticket Status Flow

1. **Pending** - Initial status when ticket is created
2. **Accepted** - Admin accepts the ticket
3. **Rejected** - Admin rejects the ticket
4. **In Progress** - Technician assigned and working
5. **Resolved** - Service completed at customer location
6. **Completed** - Final completion (products brought back to shop)

## Quotation Process

1. Admin creates quotation with items and prices
2. Customer receives quotation notification
3. Customer accepts/rejects quotation
4. If accepted, technician proceeds with service
5. Admin can generate PDF quotation for printing

## PDF Generation

The system generates professional PDF quotations including:
- Company branding and contact information
- Customer details and service information
- Itemized quotation with prices
- Terms and conditions
- Professional formatting

## Email Configuration

Configure email settings in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## CORS Configuration

The backend is configured to allow requests from the Flutter frontend:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

## Admin Interface

Access the Django admin interface at `http://localhost:8000/admin/` to:
- Manage tickets and quotations
- View user accounts
- Monitor system activity
- Generate reports

## Development

### Adding New Features
1. Create models in appropriate app
2. Create serializers for API
3. Create viewsets for API endpoints
4. Add URL patterns
5. Register models in admin
6. Create migrations

### Testing
```bash
python manage.py test
```

### Production Deployment
1. Set `DEBUG = False` in settings
2. Configure production database
3. Set up static file serving
4. Configure email settings
5. Set up SSL certificate
6. Use production WSGI server (Gunicorn)

## Support

For support and questions, contact the development team. 