from .models import Notification, Advertisement
from django.contrib.auth.models import User

def create_notification(user, notification_type, title, message, related_ad=None):
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_ad=related_ad
    )

def notify_ad_status_change(ad, status):
    if status == 'approved':
        create_notification(
            user=ad.seller,
            notification_type='ad_approved',
            title='Ad Approved',
            message=f'Your ad "{ad.title}" has been approved and is now live.',
            related_ad=ad
        )
    elif status == 'rejected':
        create_notification(
            user=ad.seller,
            notification_type='ad_rejected',
            title='Ad Rejected',
            message=f'Your ad "{ad.title}" has been rejected. Reason: {ad.rejection_reason}',
            related_ad=ad
        )

def notify_staff_new_ad(ad):
    staff_users = User.objects.filter(is_staff=True)
    for staff_user in staff_users:
        create_notification(
            user=staff_user,
            notification_type='needs_moderation',
            title='New Ad Needs Review',
            message=f'New ad "{ad.title}" needs moderation.',
            related_ad=ad
        ) 