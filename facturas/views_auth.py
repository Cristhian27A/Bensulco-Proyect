"""Vistas de autenticacion para el proyecto."""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render


def login_view(request):
    """Vista de login para usuarios internos (vendedores)."""
    if request.user.is_authenticated:
        return redirect("facturacion:nueva")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("facturacion:nueva")
    else:
        form = AuthenticationForm()

    return render(request, "auth/login.html", {"form": form})


def logout_view(request):
    """Cierra la sesion del usuario."""
    logout(request)
    return redirect("login")
