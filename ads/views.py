from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.urls import reverse_lazy
from .models import Advertisement, Category
from .forms import AdvertisementForm
from .auth_forms import UserRegistrationForm

def ad_list(request):
    ads = Advertisement.objects.filter(is_active=True)
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
            advertisement.save()
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
