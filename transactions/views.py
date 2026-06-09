"""
transactions/views.py — CRUD operations for transactions

CRUD = Create, Read, Update, Delete
These are the 4 fundamental database operations.

DATA ISOLATION PATTERN (used in EVERY view):
  Transaction.objects.filter(user=request.user)
  This ensures users only see their own data.
  NEVER do Transaction.objects.all() — that exposes everyone's data!
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm
from django.utils import timezone


@login_required
def transaction_list(request):
    """
    List all transactions for the logged-in user.
    Supports search and filter.
    Paginated: 20 per page.
    """
    # Start with all transactions for this user
    transactions = Transaction.objects.filter(user=request.user).select_related('category')

    # Search filter
    search = request.GET.get('search', '')
    if search:
        # Q objects allow OR queries: title contains search OR notes contains search
        transactions = transactions.filter(
            Q(title__icontains=search) | Q(notes__icontains=search)
        )

    # Type filter
    tx_type = request.GET.get('type', '')
    if tx_type in ['income', 'expense']:
        transactions = transactions.filter(transaction_type=tx_type)

    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        transactions = transactions.filter(category_id=category_id)

    # Date range
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        transactions = transactions.filter(date__gte=date_from)
    if date_to:
        transactions = transactions.filter(date__lte=date_to)

    # Pagination: show 20 transactions per page
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(user=request.user)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search': search,
        'tx_type': tx_type,
        'category_id': category_id,
        'date_from': date_from,
        'date_to': date_to,
        'total_count': transactions.count(),
    }
    return render(request, 'transactions/list.html', context)


@login_required
def transaction_create(request):
    """Create a new transaction."""
    if request.method == 'POST':
        # Pass user to form so it filters categories correctly
        form = TransactionForm(request.user, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)  # Don't save yet
            transaction.user = request.user          # Attach to current user
            transaction.save()                       # Now save
            messages.success(request, f'Transaction "{transaction.title}" added successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(request.user)

    return render(request, 'transactions/form.html', {
        'form': form,
        'title': 'Add Transaction',
        'button_text': 'Add Transaction'
    })


@login_required
def transaction_edit(request, pk):
    """
    Edit an existing transaction.
    get_object_or_404: if transaction doesn't exist OR doesn't belong to user → 404 error.
    This prevents users from editing other people's transactions (IDOR attack prevention).
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.user, request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(request.user, instance=transaction)

    return render(request, 'transactions/form.html', {
        'form': form,
        'title': 'Edit Transaction',
        'button_text': 'Save Changes',
        'transaction': transaction
    })


@login_required
def transaction_delete(request, pk):
    """
    Delete a transaction. Only allows POST to prevent accidental deletion via GET requests.
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)

    if request.method == 'POST':
        title = transaction.title
        transaction.delete()
        messages.success(request, f'Transaction "{title}" deleted.')
        return redirect('transaction_list')

    return render(request, 'transactions/confirm_delete.html', {'transaction': transaction})


@login_required
def category_list(request):
    """Manage categories."""
    categories = Category.objects.filter(user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, f'Category "{category.name}" created!')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'transactions/categories.html', {
        'categories': categories,
        'form': form
    })
