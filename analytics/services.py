"""
analytics/services.py — The Financial Analytics Engine

This file contains all the business logic / algorithms:
- Financial Health Score calculation
- Smart spending insights generation
- Expense forecasting
- What-If simulator

ARCHITECTURE PATTERN: Keep business logic in services.py (not views.py).
Views should be thin — they just coordinate between services and templates.
This makes code testable and reusable.
"""

from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import calendar


def get_monthly_totals(user, year=None, month=None):
    """
    Get total income and expenses for a given month.
    Default: current month.

    SQL equivalent:
    SELECT transaction_type, SUM(amount)
    FROM transactions
    WHERE user_id = ? AND MONTH(date) = ? AND YEAR(date) = ?
    GROUP BY transaction_type
    """
    from transactions.models import Transaction

    if year is None:
        year = timezone.now().year
    if month is None:
        month = timezone.now().month

    result = Transaction.objects.filter(
        user=user,
        date__year=year,
        date__month=month
    ).values('transaction_type').annotate(total=Sum('amount'))

    totals = {'income': Decimal('0'), 'expense': Decimal('0')}
    for row in result:
        totals[row['transaction_type']] = row['total'] or Decimal('0')

    totals['balance'] = totals['income'] - totals['expense']
    totals['savings'] = max(totals['balance'], Decimal('0'))
    return totals


def get_category_breakdown(user, year=None, month=None):
    """
    Get spending by category for the doughnut chart.
    Returns list of {category_name, total, color, icon}.
    """
    from transactions.models import Transaction

    if year is None:
        year = timezone.now().year
    if month is None:
        month = timezone.now().month

    breakdown = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        date__year=year,
        date__month=month
    ).values(
        'category__name',
        'category__color',
        'category__icon'
    ).annotate(
        total=Sum('amount')
    ).order_by('-total')

    result = []
    for item in breakdown:
        if item['total']:
            result.append({
                'name': item['category__name'] or 'Uncategorized',
                'total': float(item['total']),
                'color': item['category__color'] or '#6c757d',
                'icon': item['category__icon'] or 'bi-tag',
            })
    return result


def get_monthly_trend(user, months=6):
    """
    Get income vs expense trend for the last N months.
    Used for the line chart on the dashboard.

    Algorithm:
    1. Calculate the start date (N months ago)
    2. For each month in the range, sum income and expenses
    3. Return labels and datasets for Chart.js
    """
    from transactions.models import Transaction

    today = timezone.now().date()
    labels, income_data, expense_data = [], [], []

    for i in range(months - 1, -1, -1):  # months-1 down to 0 (oldest to newest)
        # Calculate which month to look at
        month = today.month - i
        year = today.year
        while month <= 0:
            month += 12
            year -= 1

        # Format label: "Jan 24", "Feb 24", etc.
        month_name = calendar.month_abbr[month]
        labels.append(f"{month_name} {str(year)[2:]}")

        # Query totals for this month
        totals = get_monthly_totals(user, year, month)
        income_data.append(float(totals['income']))
        expense_data.append(float(totals['expense']))

    return {'labels': labels, 'income': income_data, 'expenses': expense_data}


def calculate_financial_health_score(user):
    """
    ╔══════════════════════════════════════════════════════╗
    ║        FINANCIAL HEALTH SCORE ALGORITHM             ║
    ║                                                      ║
    ║  Score = Weighted sum of 4 factors (0-100 each)     ║
    ║                                                      ║
    ║  Factor 1: Savings Rate (30% weight)                ║
    ║    savings_rate = (income - expense) / income       ║
    ║    Score: 0-30 points                               ║
    ║                                                      ║
    ║  Factor 2: Expense Ratio (25% weight)               ║
    ║    expense_ratio = expense / income                 ║
    ║    Lower is better. Score: 0-25 points             ║
    ║                                                      ║
    ║  Factor 3: Budget Adherence (25% weight)            ║
    ║    % of budgets not exceeded                        ║
    ║    Score: 0-25 points                               ║
    ║                                                      ║
    ║  Factor 4: Spending Consistency (20% weight)        ║
    ║    Low variance in monthly spending = consistent    ║
    ║    Score: 0-20 points                               ║
    ╚══════════════════════════════════════════════════════╝
    """
    from transactions.models import Transaction
    from budgets.models import Budget

    today = timezone.now().date()
    year, month = today.year, today.month

    # ─── Factor 1: Savings Rate (max 30 points) ───────────────
    totals = get_monthly_totals(user, year, month)
    income = float(totals['income'])
    expense = float(totals['expense'])

    if income > 0:
        savings_rate = (income - expense) / income  # 0.0 to 1.0
        # Scale: 20%+ savings = full 30 points; 0% = 0 points
        savings_score = min(savings_rate / 0.20, 1.0) * 30
    else:
        savings_score = 0
        savings_rate = 0

    # ─── Factor 2: Expense Ratio (max 25 points) ──────────────
    if income > 0:
        expense_ratio = expense / income  # Lower is better
        # expense_ratio of 0.5 (50%) or less = full 25 points
        # expense_ratio of 1.0 (100%) or more = 0 points
        expense_score = max(0, (1 - expense_ratio / 1.0)) * 25
        expense_score = min(expense_score, 25)
    else:
        expense_score = 0
        expense_ratio = 1.0

    # ─── Factor 3: Budget Adherence (max 25 points) ───────────
    budgets = Budget.objects.filter(user=user, month=month, year=year)
    if budgets.exists():
        budgets_ok = 0
        total_budgets = budgets.count()
        for budget in budgets:
            spent = Transaction.objects.filter(
                user=user,
                category=budget.category,
                transaction_type='expense',
                date__year=year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

            if spent <= budget.amount:
                budgets_ok += 1

        budget_adherence = budgets_ok / total_budgets
        budget_score = budget_adherence * 25
    else:
        budget_score = 12.5  # Neutral if no budgets set
        budget_adherence = 0.5

    # ─── Factor 4: Spending Consistency (max 20 points) ───────
    # Get last 3 months of expenses and check variance
    monthly_expenses = []
    for i in range(1, 4):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        t = get_monthly_totals(user, y, m)
        monthly_expenses.append(float(t['expense']))

    if any(e > 0 for e in monthly_expenses):
        avg_expense = sum(monthly_expenses) / len(monthly_expenses)
        if avg_expense > 0:
            # Coefficient of variation: std_dev / mean (lower = more consistent)
            variance = sum((e - avg_expense) ** 2 for e in monthly_expenses) / len(monthly_expenses)
            std_dev = variance ** 0.5
            cv = std_dev / avg_expense  # 0 = perfectly consistent, higher = volatile
            # CV of 0.1 (10%) or less = full 20 points
            consistency_score = max(0, (1 - cv / 0.5)) * 20
        else:
            consistency_score = 10
    else:
        consistency_score = 10  # Neutral for new users

    # ─── Total Score ───────────────────────────────────────────
    total_score = int(savings_score + expense_score + budget_score + consistency_score)
    total_score = max(0, min(100, total_score))  # Clamp to 0-100

    # ─── Score Rating ──────────────────────────────────────────
    if total_score >= 80:
        rating = 'Excellent'
        color = 'success'
        emoji = '🏆'
    elif total_score >= 60:
        rating = 'Good'
        color = 'primary'
        emoji = '👍'
    elif total_score >= 40:
        rating = 'Average'
        color = 'warning'
        emoji = '📊'
    else:
        rating = 'Needs Improvement'
        color = 'danger'
        emoji = '⚠️'

    return {
        'total_score': total_score,
        'rating': rating,
        'color': color,
        'emoji': emoji,
        'factors': {
            'savings': {'score': round(savings_score, 1), 'max': 30, 'rate': round(savings_rate * 100, 1)},
            'expense': {'score': round(expense_score, 1), 'max': 25, 'ratio': round(expense_ratio * 100, 1)},
            'budget': {'score': round(budget_score, 1), 'max': 25, 'adherence': round(budget_adherence * 100, 1)},
            'consistency': {'score': round(consistency_score, 1), 'max': 20},
        }
    }


def generate_smart_insights(user):
    """
    Generate personalized financial insights by comparing this month vs last month.

    Algorithm:
    1. Get this month's category spending
    2. Get last month's category spending
    3. Compare and generate human-readable insights

    No AI API needed — pure Python analytics.
    """
    from transactions.models import Transaction

    today = timezone.now().date()
    this_month = today.month
    this_year = today.year

    last_month = this_month - 1
    last_year = this_year
    if last_month == 0:
        last_month = 12
        last_year -= 1

    # Get spending by category for both months
    def get_category_spending(year, month):
        from django.db.models import Sum as _Sum
        return dict(
            Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date__year=year,
                date__month=month
            ).values('category__name').annotate(
                total=_Sum('amount')
            ).values_list('category__name', 'total')
        )

    this_month_spending = get_category_spending(this_year, this_month)
    last_month_spending = get_category_spending(last_year, last_month)

    insights = []

    # ─── Insight 1: Highest expense category ──────────────────
    if this_month_spending:
        top_category = max(this_month_spending, key=this_month_spending.get)
        top_amount = this_month_spending[top_category]
        insights.append({
            'type': 'info',
            'icon': 'bi-bar-chart',
            'text': f'"{top_category or "Uncategorized"}" is your highest expense this month at ₹{float(top_amount):,.0f}.',
            'color': 'primary'
        })

    # ─── Insight 2: Category increases/decreases ──────────────
    for category, this_amount in this_month_spending.items():
        if category in last_month_spending and last_month_spending[category]:
            last_amount = last_month_spending[category]
            change_pct = ((float(this_amount) - float(last_amount)) / float(last_amount)) * 100

            if change_pct > 15:
                insights.append({
                    'type': 'warning',
                    'icon': 'bi-arrow-up-circle',
                    'text': f'You spent {change_pct:.0f}% more on "{category or "Uncategorized"}" compared to last month.',
                    'color': 'warning'
                })
            elif change_pct < -10:
                insights.append({
                    'type': 'success',
                    'icon': 'bi-arrow-down-circle',
                    'text': f'Great! "{category or "Uncategorized"}" spending decreased by {abs(change_pct):.0f}% from last month.',
                    'color': 'success'
                })

    # ─── Insight 3: Savings trend ─────────────────────────────
    this_totals = get_monthly_totals(user, this_year, this_month)
    last_totals = get_monthly_totals(user, last_year, last_month)

    this_savings = float(this_totals['savings'])
    last_savings = float(last_totals['savings'])

    if last_savings > 0 and this_savings > last_savings:
        improvement = ((this_savings - last_savings) / last_savings) * 100
        insights.append({
            'type': 'success',
            'icon': 'bi-piggy-bank',
            'text': f'Your savings improved by {improvement:.0f}% compared to last month! Keep it up! 💪',
            'color': 'success'
        })
    elif last_savings > 0 and this_savings < last_savings:
        decline = ((last_savings - this_savings) / last_savings) * 100
        insights.append({
            'type': 'warning',
            'icon': 'bi-exclamation-triangle',
            'text': f'Your savings declined by {decline:.0f}% from last month. Consider reviewing your expenses.',
            'color': 'warning'
        })

    # ─── Insight 4: Budget alerts ─────────────────────────────
    from budgets.models import Budget
    
    budgets = Budget.objects.filter(user=user, month=this_month, year=this_year)
    for budget in budgets:
        spent = Transaction.objects.filter(
            user=user,
            category=budget.category,
            transaction_type='expense',
            date__year=this_year,
            date__month=this_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        utilization = float(spent) / float(budget.amount) if budget.amount > 0 else 0

        if utilization > 1.0:
            over_by = float(spent) - float(budget.amount)
            insights.append({
                'type': 'danger',
                'icon': 'bi-exclamation-octagon',
                'text': f'⚠️ {budget.category.name} budget exceeded by ₹{over_by:,.0f}!',
                'color': 'danger'
            })
        elif utilization > 0.85:
            insights.append({
                'type': 'warning',
                'icon': 'bi-bell',
                'text': f'{budget.category.name} budget is {utilization*100:.0f}% used. Nearing the limit!',
                'color': 'warning'
            })

    if not insights:
        insights.append({
            'type': 'info',
            'icon': 'bi-lightbulb',
            'text': 'Add more transactions to see personalized insights!',
            'color': 'secondary'
        })

    return insights[:6]  # Return top 6 insights


def forecast_month_end_spending(user):
    """
    ╔══════════════════════════════════════════════════════════╗
    ║           EXPENSE FORECASTING ALGORITHM                 ║
    ║                                                          ║
    ║  Formula:                                               ║
    ║    daily_rate = current_spend / days_elapsed            ║
    ║    forecasted = daily_rate × total_days_in_month        ║
    ║                                                          ║
    ║  Weighted with historical average:                      ║
    ║    forecast = (daily_forecast × 0.6) + (hist_avg × 0.4)║
    ║                                                          ║
    ║  This gives 60% weight to current behavior and         ║
    ║  40% to historical pattern for better accuracy.         ║
    ╚══════════════════════════════════════════════════════════╝
    """
    from transactions.models import Transaction

    today = timezone.now().date()
    year, month = today.year, today.month

    # Days elapsed this month (avoid division by zero)
    days_elapsed = max(today.day, 1)
    days_in_month = calendar.monthrange(year, month)[1]
    days_remaining = days_in_month - days_elapsed

    # Current month spending so far
    current_spend = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        date__year=year,
        date__month=month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

    current_spend = float(current_spend)

    # Daily spending rate this month
    daily_rate = current_spend / days_elapsed

    # Simple projection: continue at current rate
    simple_forecast = daily_rate * days_in_month

    # Historical average (last 3 months)
    historical_monthly = []
    for i in range(1, 4):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        t = get_monthly_totals(user, y, m)
        if float(t['expense']) > 0:
            historical_monthly.append(float(t['expense']))

    if historical_monthly:
        historical_avg = sum(historical_monthly) / len(historical_monthly)
        # Weighted forecast: 60% current behavior + 40% historical
        forecasted_spend = (simple_forecast * 0.6) + (historical_avg * 0.4)
    else:
        forecasted_spend = simple_forecast
        historical_avg = simple_forecast

    # Accuracy: how much data do we have? More days elapsed = more accurate
    accuracy = min(int((days_elapsed / days_in_month) * 100), 95)

    return {
        'current_spend': round(current_spend, 2),
        'forecasted_spend': round(forecasted_spend, 2),
        'daily_rate': round(daily_rate, 2),
        'days_elapsed': days_elapsed,
        'days_remaining': days_remaining,
        'days_in_month': days_in_month,
        'accuracy': accuracy,
        'historical_avg': round(historical_avg, 2) if historical_monthly else 0,
        'month_name': calendar.month_name[month],
        'year': year,
    }


def what_if_simulator(user, category_name, reduction_pct):
    """
    What-If Financial Simulator.

    Given: User wants to reduce spending on <category> by <reduction_pct>%
    Calculate: New savings, new annual savings, new financial score.

    Example:
      Category: Food, Current: ₹8000, Reduce by: 20%
      Savings: ₹1600/month, ₹19200/year
    """
    from transactions.models import Transaction, Category

    today = timezone.now().date()
    year, month = today.year, today.month

    totals = get_monthly_totals(user, year, month)
    current_income = float(totals['income'])
    current_expense = float(totals['expense'])
    current_savings = float(totals['savings'])

    # Find current spending on this category
    current_category_spend = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        category__name__iexact=category_name,
        date__year=year,
        date__month=month
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    current_category_spend = float(current_category_spend)

    # Calculate savings from reduction
    monthly_saving = current_category_spend * (reduction_pct / 100)
    new_monthly_expenses = current_expense - monthly_saving
    new_monthly_savings = current_income - new_monthly_expenses
    annual_saving = monthly_saving * 12

    # Estimate new financial score (simplified)
    health = calculate_financial_health_score(user)
    current_score = health['total_score']

    if current_income > 0:
        new_savings_rate = new_monthly_savings / current_income
        # Rough estimate: each 1% improvement in savings rate ≈ 0.5 score points
        improvement = (new_savings_rate - (current_savings / current_income if current_income > 0 else 0)) * 50
        projected_score = min(100, int(current_score + improvement))
    else:
        projected_score = current_score

    return {
        'category': category_name,
        'reduction_pct': reduction_pct,
        'current_category_spend': round(current_category_spend, 2),
        'monthly_saving': round(monthly_saving, 2),
        'new_monthly_expenses': round(new_monthly_expenses, 2),
        'new_monthly_savings': round(new_monthly_savings, 2),
        'annual_saving': round(annual_saving, 2),
        'current_score': current_score,
        'projected_score': projected_score,
        'score_improvement': projected_score - current_score,
    }
