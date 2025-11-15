from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from .models import User, Role
from .forms import UserRegistrationForm, UserUpdateForm, LoginForm, RoleForm


class CustomLoginView(LoginView):
    """Custom login view."""
    template_name = 'users/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


@login_required
def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')


def is_admin(user):
    """Check if user is admin."""
    return user.is_superuser or (user.role and user.role.can_manage_users)


@login_required
@user_passes_test(is_admin)
def user_list(request):
    """List all users."""
    users = User.objects.select_related('role').all()
    return render(request, 'users/user_list.html', {'users': users})


@login_required
@user_passes_test(is_admin)
def user_create(request):
    """Create new user."""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('users:user_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/user_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def user_edit(request, pk):
    """Edit existing user."""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('users:user_list')
    else:
        form = UserUpdateForm(instance=user)
    return render(request, 'users/user_form.html', {'form': form, 'action': 'Edit'})


@login_required
@user_passes_test(is_admin)
def user_delete(request, pk):
    """Delete user."""
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('users:user_list')
    return render(request, 'users/user_confirm_delete.html', {'user': user})


@login_required
@user_passes_test(is_admin)
def role_list(request):
    """List all roles."""
    roles = Role.objects.all()
    return render(request, 'users/role_list.html', {'roles': roles})


@login_required
@user_passes_test(is_admin)
def role_create(request):
    """Create new role."""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role created successfully.')
            return redirect('users:role_list')
    else:
        form = RoleForm()
    return render(request, 'users/role_form.html', {'form': form, 'action': 'Create'})


@login_required
@user_passes_test(is_admin)
def role_edit(request, pk):
    """Edit existing role."""
    role = get_object_or_404(Role, pk=pk)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Role updated successfully.')
            return redirect('users:role_list')
    else:
        form = RoleForm(instance=role)
    return render(request, 'users/role_form.html', {'form': form, 'action': 'Edit'})


@login_required
def profile_view(request):
    """View user profile."""
    return render(request, 'users/profile.html', {'user': request.user})
