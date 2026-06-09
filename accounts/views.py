"""
accounts/views.py — Authentication Views

A VIEW is a Python function (or class) that:
1. Receives an HTTP request
2. Processes business logic
3. Returns an HTTP response (usually rendered HTML)

Security pattern used everywhere:
  @login_required — redirects unauthenticated users to LOGIN_URL
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile


def landing_page(request):
    """
    The public homepage at /.
    If user is already logged in → redirect to dashboard.
    Otherwise → show the landing/marketing page.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')


def register_view(request):
    """
    Handles GET (show form) and POST (submit form) for registration.

    GET:  Show empty registration form
    POST: Validate → save → log in → redirect to dashboard

    This is the standard Django form handling pattern.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user to the database
            user = form.save()
            # Log them in immediately after registration
            login(request, user)
            messages.success(request, f'Welcome to SmartExpense, {user.username}! 🎉')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        # GET request — show empty form
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Custom login view.
    We build our own instead of using Django's built-in to have full control over the UI.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # authenticate() checks credentials against the database
        # Returns User object if valid, None if invalid
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Creates a session for this user
            messages.success(request, f'Welcome back, {user.username}!')
            # After login, redirect to the page they were trying to access,
            # or fall back to dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """
    Log out the user and destroy their session.
    Only allow POST requests to prevent CSRF logout attacks.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out successfully.')
    return redirect('landing')


@login_required
def profile_view(request):
    """
    View and update user profile.
    @login_required: if not logged in, redirect to /accounts/login/
    """
    # Get or create the UserProfile (in case it was somehow not created at registration)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update the User model fields
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.email = form.cleaned_data.get('email', '')
            request.user.save()

            # Save the profile
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        # Pre-fill form with existing data
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = UserProfileForm(instance=profile, initial=initial_data)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})
