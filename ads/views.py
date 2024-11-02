from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Advertisement, Category

def ad_list(request):
    ads = Advertisement.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'advertisements/list.html', {
        'ads': ads,
        'categories': categories
    })

def ad_detail(request, pk):
    ad = get_object_or_404(Advertisement, pk=pk, is_active=True)
    return render(request, 'advertisements/detail.html', {'ad': ad})

@login_required
def ad_create(request):
    if request.method == 'POST':
        # Handle form submission
        pass
    return render(request, 'advertisements/create.html')
