from django.shortcuts import render
from .models import ResourceOpportunity, CareerStep
from django.db.models import Q
# Create your views here.

def resource_dashboard(request):
    resources = ResourceOpportunity.objects.all()  # Fetch all opportunities
    category_filter = request.GET.get('category')

    if category_filter:
        resources = resources.filter(category=category_filter)

    categories = [choice[0] for choice in ResourceOpportunity.CATEGORY_CHOICES]

    context = {
        'resources': resources,
        'categories': categories,
        'selected_category': category_filter
    }
    return render(request, 'uncc-resource-dashboard.html', context)

def career_confidence_boost(request):
    return render (request, 'uncc-career-confidence-boost.html')

def visualize_trajectory(request):
    role = request.GET.get('role', 'Software Developer')  # Default for now
    steps = CareerStep.objects.filter(role=role)
    roles = CareerStep.objects.values_list('role', flat=True).distinct()

    return render(request, 'uncc_career_trajectory.html', {
        'steps': steps,
        'roles': roles,
        'selected_role': role
    })

