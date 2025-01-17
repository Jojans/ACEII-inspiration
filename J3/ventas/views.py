from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirigir a la vista de lobby después de un login exitoso
            return redirect('lobby')

    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def perfil_usuario(request):
    return render(request, 'perfil.html', {
        'user': request.user
    })

@login_required
def lobby(request):
    if request.user.is_staff:
        return render(request, 'staff_dashboard.html')
    else:
        return render(request, 'user_dashboard.html')

@login_required
def administrar_sistema(request):
    return render(request, 'administrar_sistema.html')

@login_required
def ventas(request):
    return render(request, 'ventas.html')

@login_required
def administrar_usuarios(request):
    usuarios = User.objects.all()

    # Agregar usuario
    if 'add_user' in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_staff = request.POST.get('is_staff') == 'True'

        if username and password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "El nombre de usuario ya está registrado. Por favor, elige otro.")
                return redirect('administrar_usuarios')

            user = User.objects.create_user(username=username, password=password, email=email)
            user.first_name = first_name
            user.last_name = last_name
            user.is_staff = is_staff
            messages.success(request, f"{user.username} agregado correctamente.")
            user.save()

        return redirect('administrar_usuarios')
                
    # Eliminar usuario
    if 'delete_user' in request.POST:
        user_id = request.POST.get('user_id')  # Obtener el id del usuario
        if user_id:
            try:
                user = User.objects.get(id=user_id)  # Buscar al usuario por id
                user.delete()  # Eliminar usuario
                messages.success(request, f"Usuario {user.username} eliminado correctamente.")
            except User.DoesNotExist:
                messages.error(request, f"El usuario no existe.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al eliminar el usuario: {str(e)}")

        return redirect('administrar_usuarios')
    
    # Cambiar contraseña
    if "change_password" in request.POST:
        user_id = request.POST.get("user_id")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if user_id and new_password and confirm_password:
            if new_password == confirm_password:
                try:
                    user = User.objects.get(id=user_id)
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, f"La contraseña para {user.username} ha sido cambiada exitosamente.")
                except User.DoesNotExist:
                    messages.error(request, "El usuario no existe.")
            else:
                messages.error(request, "Las contraseñas no coinciden.")
        else:
            messages.error(request, "Todos los campos son obligatorios.")
        
        return redirect('administrar_usuarios')
    
    return render(request, 'administrar_usuarios.html', {'usuarios': usuarios})

@login_required
def historial_ventas(request):
    return render(request, 'historial_ventas.html')

@login_required
def administrar_inventario(request):
    return render(request, 'administrar_inventario.html')

