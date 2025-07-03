from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TechnicianProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician_profile')
    mobile = models.CharField(max_length=20)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.TextField()
    profile_photo = models.ImageField(upload_to='technician_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name()
