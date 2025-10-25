# api/views_auth.py
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.shortcuts import render, redirect


def signup_view(request):
    """
    Vista para registrar nuevos usuarios con el formulario predeterminado de Django.
    Incluye validación, auto-login y mensajes de retroalimentación.
    """
    # Si ya está autenticado, lo redirigimos a inicio
    if request.user.is_authenticated:
        return redirect('/')

    # Si se envió el formulario
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Guardar usuario
            user = form.save()
            # Iniciar sesión automáticamente
            login(request, user)
            messages.success(request, "🎉 ¡Tu cuenta fue creada exitosamente! Bienvenido a EduVision.")
            return redirect('/')  # Redirige tras crear cuenta
        else:
            # Errores de validación
            messages.error(request, "Por favor, corrige los errores resaltados abajo.")
            return render(request, 'registration/signup.html', {'form': form})

    # Si la solicitud es GET (mostrar formulario)
    elif request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

    # Para cualquier otro método (por seguridad)
    else:
        messages.error(request, "Método no permitido.")
        return redirect('/accounts/login/')
