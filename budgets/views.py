from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from .models import Budget
from .forms import BudgetForm
from transactions.models import Transaction
from datetime import datetime   

@login_required
def budget_list(request):
    today = timezone.now().date()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))
    budgets = Budget.objects.filter(user=request.user, month=month, year=year).select_related('category')
    budget_data = []
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=request.user, category=budget.category,
            transaction_type='expense', date__year=year, date__month=month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        utilization = float(spent) / float(budget.amount) * 100 if budget.amount > 0 else 0
        budget_data.append({
            'budget': budget, 'spent': spent,
            'remaining': max(budget.amount - spent, Decimal('0')),
            'utilization': round(min(utilization, 100), 1),
            'over_budget': spent > budget.amount,
        })
    return render(request, 'budgets/list.html', {
        'budget_data': budget_data, 'month': month, 'year': year,
        'month_name': datetime(year, month, 1).strftime('%B %Y')
    })

@login_required
def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.user, request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created!')
            return redirect('budget_list')
    else:
        form = BudgetForm(request.user)
    return render(request, 'budgets/form.html', {'form': form, 'title': 'Create Budget'})

@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted.')
        return redirect('budget_list')
    return render(request, 'budgets/confirm_delete.html', {'budget': budget})
