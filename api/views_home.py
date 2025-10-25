from django.shortcuts import render

def home_view(request):
    """
    Página principal (landing page) pública de EduVision.
    Siempre se muestra, esté o no autenticado el usuario.
    """
    return render(request, "home.html")
