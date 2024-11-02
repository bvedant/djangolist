from .models import Advertisement

def admin_context(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.is_staff:
            context['pending_count'] = Advertisement.objects.filter(
                status='pending',
                is_active=True
            ).count()
        context['unread_notifications'] = request.user.notification_set.filter(
            read=False
        ).count()
    return context 