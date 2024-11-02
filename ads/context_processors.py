from .models import Advertisement

def admin_context(request):
    if request.user.is_authenticated and request.user.is_staff:
        pending_count = Advertisement.objects.filter(
            status='pending',
            is_active=True
        ).count()
        return {'pending_count': pending_count}
    return {} 