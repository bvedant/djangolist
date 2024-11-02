from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Advertisement, Category, DeletionRequest
from .forms import AdvertisementForm, DeletionRequestForm
from .auth_forms import UserRegistrationForm

def ad_list(request):
    ads = Advertisement.objects.filter(is_active=True, status='approved')
    categories = Category.objects.all()
    return render(request, 'ads/list.html', {
        'ads': ads,
        'categories': categories
    })

def ad_detail(request, slug):
    ad = get_object_or_404(Advertisement, slug=slug, is_active=True)
    return render(request, 'ads/detail.html', {'ad': ad})

@login_required
def ad_create(request):
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.seller = request.user
            # Set initial status
            if request.user.is_staff:
                advertisement.status = 'approved'
            advertisement.save()
            
            if advertisement.status == 'pending':
                messages.success(
                    request,
                    'Thank you! Your ad has been submitted and is pending approval. '
                    'Please check back later to see if it has been approved.'
                )
            else:
                messages.success(request, 'Your ad has been posted successfully.')
            return redirect('ads:detail', slug=advertisement.slug)
    else:
        form = AdvertisementForm()
    
    return render(request, 'ads/create.html', {'form': form})

@login_required
def ad_edit(request, slug):
    advertisement = get_object_or_404(Advertisement, slug=slug)
    
    # Check if the user is the seller
    if request.user != advertisement.seller:
        return redirect('ads:detail', slug=slug)
    
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=advertisement)
        if form.is_valid():
            form.save()
            return redirect('ads:detail', slug=slug)
    else:
        form = AdvertisementForm(instance=advertisement)
    
    return render(request, 'ads/edit.html', {'form': form, 'ad': advertisement})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('ads:list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def request_deletion(request, slug):
    ad = get_object_or_404(Advertisement, slug=slug)
    
    # Redirect admins since they can delete directly
    if request.user.is_staff:
        return redirect('ads:detail', slug=slug)
    
    # Check if user is the seller
    if request.user != ad.seller:
        return redirect('ads:detail', slug=slug)
    
    # Check if there's already a pending request
    existing_request = DeletionRequest.objects.filter(
        advertisement=ad,
        status='pending'
    ).exists()
    
    if existing_request:
        messages.warning(request, 'A deletion request for this ad is already pending.')
        return redirect('ads:detail', slug=slug)
    
    if request.method == 'POST':
        form = DeletionRequestForm(request.POST)
        if form.is_valid():
            deletion_request = form.save(commit=False)
            deletion_request.advertisement = ad
            deletion_request.requested_by = request.user
            deletion_request.save()
            messages.success(request, 'Your deletion request has been submitted.')
            return redirect('ads:detail', slug=slug)
    else:
        form = DeletionRequestForm()
    
    return render(request, 'ads/request_deletion.html', {
        'form': form,
        'ad': ad
    })

@login_required
def ad_delete(request, slug):
    ad = get_object_or_404(Advertisement, slug=slug)
    
    # Only allow staff members to delete directly
    if not request.user.is_staff:
        return redirect('ads:detail', slug=slug)
    
    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Advertisement has been deleted.')
        return redirect('ads:list')
    
    return redirect('ads:detail', slug=slug)

@login_required
def ad_approve(request, slug):
    if not request.user.is_staff:
        return redirect('ads:list')
        
    ad = get_object_or_404(Advertisement, slug=slug)
    ad.status = 'approved'
    ad.save()
    messages.success(request, 'Advertisement has been approved.')
    return redirect('ads:detail', slug=slug)

@login_required
def ad_reject(request, slug):
    if not request.user.is_staff:
        return redirect('ads:list')
        
    ad = get_object_or_404(Advertisement, slug=slug)
    if request.method == 'POST':
        ad.status = 'rejected'
        ad.rejection_reason = request.POST.get('reason', '')
        ad.save()
        messages.success(request, 'Advertisement has been rejected.')
        return redirect('ads:detail', slug=slug)
    
    return render(request, 'ads/reject.html', {'ad': ad})

@login_required
def admin_dashboard(request):
    # Redirect non-staff users
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('ads:list')
    
    # Get pending ads, ordered by oldest first
    pending_ads = Advertisement.objects.filter(
        status='pending',
        is_active=True
    ).order_by('created_at')
    
    # Get recently rejected ads
    rejected_ads = Advertisement.objects.filter(
        status='rejected',
        is_active=True
    ).order_by('-updated_at')[:10]  # Limit to 10 most recent
    
    context = {
        'pending_ads': pending_ads,
        'rejected_ads': rejected_ads,
        'pending_count': pending_ads.count(),
        'rejected_count': rejected_ads.count(),
    }
    
    return render(request, 'ads/admin_dashboard.html', context)
