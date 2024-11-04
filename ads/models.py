from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid
from django.utils import timezone
from datetime import timedelta


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Advertisement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            uuid_start = str(self.id)[:8]
            self.slug = f"{slugify(self.title)}-{uuid_start}"
        
        # Auto-approve ads created by staff members
        if self.seller.is_staff and self.status == 'pending':
            self.status = 'approved'
            
        super().save(*args, **kwargs)

    @property
    def formatted_price(self):
        from django.contrib.humanize.templatetags.humanize import intcomma
        return intcomma(int(self.price))

    def is_new(self):
        return (timezone.now() - self.created_at) < timedelta(hours=24)

class DeletionRequest(models.Model):
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )

    def __str__(self):
        return f"Deletion request for {self.advertisement.title}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('ad_approved', 'Ad Approved'),
        ('ad_rejected', 'Ad Rejected'),
        ('deletion_approved', 'Deletion Request Approved'),
        ('deletion_rejected', 'Deletion Request Rejected'),
        ('needs_moderation', 'Needs Moderation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    related_ad = models.ForeignKey(
        'Advertisement', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}"
