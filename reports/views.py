"""
reports/views.py — CSV, Excel, and PDF Export

These views generate downloadable files instead of rendering HTML.
The response has special headers telling the browser to download the file.
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from transactions.models import Transaction
from django.db.models import Sum
import csv
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from decimal import Decimal

@login_required
def reports_home(request):
    return render(request, 'reports/home.html')

@login_required
def export_csv(request):
    """Export transactions as CSV."""
    user = request.user
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))

    transactions = Transaction.objects.filter(
        user=user, date__year=year, date__month=month
    ).select_related('category').order_by('date')

    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="transactions_{year}_{month:02d}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Title', 'Category', 'Type', 'Amount (₹)', 'Notes'])

    for t in transactions:
        writer.writerow([
            t.date.strftime('%Y-%m-%d'),
            t.title,
            t.category.name if t.category else 'Uncategorized',
            t.get_transaction_type_display(),
            float(t.amount),
            t.notes or '',
        ])

    return response

@login_required
def export_excel(request):
    """Export transactions as Excel with formatting."""
    user = request.user
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))

    transactions = Transaction.objects.filter(
        user=user, date__year=year, date__month=month
    ).select_related('category').order_by('date')

    wb = openpyxl.Workbook()
    ws = wb.active
    import calendar

    month_name = calendar.month_name[int(month)]
    ws.title = f"Transactions {month_name} {year}"
    
    

    # Header row with styling
    headers = ['Date', 'Title', 'Category', 'Type', 'Amount (₹)', 'Notes']
    header_fill = PatternFill(start_color='1a1f2e', end_color='1a1f2e', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')

    # Data rows
    for row_num, t in enumerate(transactions, 2):
        ws.cell(row=row_num, column=1, value=t.date.strftime('%Y-%m-%d'))
        ws.cell(row=row_num, column=2, value=t.title)
        ws.cell(row=row_num, column=3, value=t.category.name if t.category else 'Uncategorized')
        ws.cell(row=row_num, column=4, value=t.get_transaction_type_display())
        amount_cell = ws.cell(row=row_num, column=5, value=float(t.amount))
        # Color income green, expense red
        if t.transaction_type == 'income':
            amount_cell.font = Font(color='198754')
        else:
            amount_cell.font = Font(color='DC3545')
        ws.cell(row=row_num, column=6, value=t.notes or '')

    # Auto-fit columns
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    # Summary section
    ws.append([])
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    ws.append(['', '', '', 'Total Income:', float(total_income)])
    ws.append(['', '', '', 'Total Expense:', float(total_expense)])
    ws.append(['', '', '', 'Balance:', float(total_income) - float(total_expense)])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="transactions_{year}_{month:02d}.xlsx"'
    return response

