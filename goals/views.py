from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import SavingsGoal
from django import forms

class GoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['name', 'description', 'target_amount', 'current_amount', 'target_date', 'icon', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Laptop, Vacation'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'current_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'icon': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }

@login_required
def goal_list(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, 'goals/list.html', {'goals': goals})

@login_required
def goal_create(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, f'Goal "{goal.name}" created!')
            return redirect('goal_list')
    else:
        form = GoalForm()
    return render(request, 'goals/form.html', {'form': form, 'title': 'Create Goal'})

@login_required
def goal_edit(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated!')
            return redirect('goal_list')
    else:
        form = GoalForm(instance=goal)
    return render(request, 'goals/form.html', {'form': form, 'title': 'Edit Goal', 'goal': goal})

@login_required
def goal_delete(request, pk):
    goal = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        goal.delete()
        messages.success(request, 'Goal deleted.')
        return redirect('goal_list')
    return render(request, 'goals/confirm_delete.html', {'goal': goal})
