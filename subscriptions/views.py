from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Subscription
from django import forms

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['name', 'amount', 'frequency', 'renewal_date', 'notes', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Netflix'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'frequency': forms.Select(attrs={'class': 'form-select'}),
            'renewal_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }

@login_required
def subscription_list(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    total_monthly = sum(s.monthly_cost for s in subscriptions if s.status == 'active')
    return render(request, 'subscriptions/list.html', {
        'subscriptions': subscriptions, 'total_monthly': round(total_monthly, 2)
    })

@login_required
def subscription_create(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.user = request.user
            sub.save()
            messages.success(request, f'Subscription "{sub.name}" added!')
            return redirect('subscription_list')
    else:
        form = SubscriptionForm()
    return render(request, 'subscriptions/form.html', {'form': form, 'title': 'Add Subscription'})

@login_required
def subscription_edit(request, pk):
    sub = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SubscriptionForm(request.POST, instance=sub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subscription updated!')
            return redirect('subscription_list')
    else:
        form = SubscriptionForm(instance=sub)
    return render(request, 'subscriptions/form.html', {'form': form, 'title': 'Edit Subscription', 'sub': sub})

@login_required
def subscription_delete(request, pk):
    sub = get_object_or_404(Subscription, pk=pk, user=request.user)
    if request.method == 'POST':
        sub.delete()
        messages.success(request, 'Subscription deleted.')
        return redirect('subscription_list')
    return render(request, 'subscriptions/confirm_delete.html', {'sub': sub})
