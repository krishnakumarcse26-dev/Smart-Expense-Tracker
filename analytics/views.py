"""
analytics/views.py — Dashboard and Analytics Views

The dashboard aggregates data from all other apps
and passes it to the template for Chart.js visualization.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from . import services
import json


@login_required
def dashboard(request):
    """
    Main dashboard — shows overview of user's financial health.
    This is the most important page of the app.
    """
    user = request.user
    today = timezone.now().date()

    # ─── Core financial data ───────────────────────────────────
    monthly_totals = services.get_monthly_totals(user)
    category_breakdown = services.get_category_breakdown(user)
    monthly_trend = services.get_monthly_trend(user, months=6)
    health_score = services.calculate_financial_health_score(user)
    insights = services.generate_smart_insights(user)

    # ─── Recent transactions (last 5) ─────────────────────────
    from transactions.models import Transaction
    recent_transactions = Transaction.objects.filter(
        user=user
    ).select_related('category').order_by('-date', '-created_at')[:5]

    # ─── Active subscriptions ─────────────────────────────────
    from subscriptions.models import Subscription
    upcoming_subscriptions = Subscription.objects.filter(
        user=user,
        status='active'
    ).order_by('renewal_date')[:3]

    # ─── Active goals ─────────────────────────────────────────
    from goals.models import SavingsGoal
    active_goals = SavingsGoal.objects.filter(
        user=user,
        status='active'
    ).order_by('target_date')[:3]

    # ─── Budgets with utilization ─────────────────────────────
    from budgets.models import Budget
    from transactions.models import Transaction
    from django.db.models import Sum
    from decimal import Decimal

    budgets = Budget.objects.filter(
        user=user,
        month=today.month,
        year=today.year
    ).select_related('category')

    budget_data = []
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=user,
            category=budget.category,
            transaction_type='expense',
            date__year=today.year,
            date__month=today.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        utilization = float(spent) / float(budget.amount) * 100 if budget.amount > 0 else 0
        budget_data.append({
            'budget': budget,
            'spent': spent,
            'remaining': max(budget.amount - spent, Decimal('0')),
            'utilization': round(min(utilization, 100), 1),
            'over_budget': spent > budget.amount,
        })

    context = {
        'monthly_totals': monthly_totals,
        'health_score': health_score,
        'insights': insights,
        'recent_transactions': recent_transactions,
        'upcoming_subscriptions': upcoming_subscriptions,
        'active_goals': active_goals,
        'budget_data': budget_data,

        # JSON for Chart.js (must be serialized)
        'chart_categories': json.dumps([c['name'] for c in category_breakdown]),
        'chart_amounts': json.dumps([c['total'] for c in category_breakdown]),
        'chart_colors': json.dumps([c['color'] for c in category_breakdown]),
        'trend_labels': json.dumps(monthly_trend['labels']),
        'trend_income': json.dumps(monthly_trend['income']),
        'trend_expenses': json.dumps(monthly_trend['expenses']),

        'today': today,
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'analytics/dashboard.html', context)


@login_required
def forecast_view(request):
    """Expense forecasting page."""
    forecast = services.forecast_month_end_spending(request.user)
    return render(request, 'analytics/forecast.html', {'forecast': forecast})


@login_required
def what_if_view(request):
    """What-If simulator page."""
    from transactions.models import Category
    categories = Category.objects.filter(user=request.user, category_type__in=['expense', 'both'])
    result = None

    if request.method == 'POST':
        category_name = request.POST.get('category', '')
        try:
            reduction_pct = float(request.POST.get('reduction_pct', 10))
            reduction_pct = max(1, min(100, reduction_pct))
        except ValueError:
            reduction_pct = 10

        if category_name:
            result = services.what_if_simulator(request.user, category_name, reduction_pct)

    return render(request, 'analytics/what_if.html', {
        'categories': categories,
        'result': result
    })


@login_required
def health_score_view(request):
    """Detailed financial health score breakdown."""
    health_score = services.calculate_financial_health_score(request.user)
    return render(request, 'analytics/health_score.html', {'health_score': health_score})
