from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .forms import UserUpdateForm, ProfileUpdateForm
from django.core.exceptions import PermissionDenied
from .models import Profile

User = get_user_model()


# ---------------- SIGNUP ----------------
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('signup')

        # ✅ Create user only
        user = User.objects.create_user(username=username, email=email, password=password1)

        if role == 'provider':
            user.is_provider = True
        else:
            user.is_customer = True
        user.save()

        # ✅ Profile signal से पहले ही बन चुका है, अब सिर्फ update करो
        user.profile.role = role
        user.profile.save()

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, 'accounts/signup.html')


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Redirect by role
            if user.is_provider:
                return redirect('provider_dashboard')
            elif user.is_customer:
                return redirect('customer_dashboard')
            else:
                return redirect('home')

        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'accounts/login.html')


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect('home')


# ---------------- DASHBOARDS ----------------
@login_required
def provider_dashboard(request):
    if not request.user.is_provider:
        raise PermissionDenied
    return render(request, 'accounts/provider_dashboard.html')


@login_required
def customer_dashboard(request):
    if not request.user.is_customer:
        raise PermissionDenied
    return render(request, 'accounts/customer_dashboard.html')


# ---------------- PROFILE ----------------
@login_required
def profile_view(request):
    user = request.user

    # Auto-create profile if missing (fixes "CustomUser has no profile" error)
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile.html', context)
