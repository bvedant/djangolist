from django.contrib import admin
from .models import Category, Advertisement, DeletionRequest

# Register your models here.
admin.site.register(Category)
admin.site.register(Advertisement)

class DeletionRequestAdmin(admin.ModelAdmin):
    list_display = ['advertisement', 'requested_by', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['advertisement__title', 'requested_by__username']

admin.site.register(DeletionRequest, DeletionRequestAdmin)
