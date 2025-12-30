from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def register_view(request):
    """Представление для регистрации"""
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect("accounts:profile")
    else:
        form = UserRegistrationForm()
    
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """Представление для входа"""
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            next_url = request.GET.get("next", "accounts:profile")
            # Исправляем next_url если это строка с именем маршрута
            if next_url and not next_url.startswith("/"):
                from django.urls import reverse
                try:
                    next_url = reverse(next_url)
                except:
                    next_url = "accounts:profile"
            return redirect(next_url)
    else:
        form = UserLoginForm()
    
    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    """Представление для выхода"""
    logout(request)
    messages.success(request, "Вы успешно вышли из системы.")
    return redirect("main:home")


@login_required
def profile_view(request):
    """Представление личного кабинета"""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен!")
            return redirect("accounts:profile")
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, "accounts/profile.html", {"form": form})
