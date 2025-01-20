from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Producto
from django.http import JsonResponse  


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
    productos = Producto.objects.all()
    if request.method == 'POST':
        if 'set_caja_inicial' in request.POST:
            valor_caja_inicial = request.POST.get('valor_caja_inicial')
            
            # Convertir el valor a float y formatearlo como dinero
            valor_caja_inicial = float(valor_caja_inicial)
            request.session['caja_inicial'] = f"${valor_caja_inicial:,.2f}"
            
            return redirect('ventas')
    
    # Obtener el valor de la caja inicial (si existe)
    caja_inicial = request.session.get('caja_inicial', '')

    return render(request, 'ventas.html', {'caja_inicial': caja_inicial, 'productos': productos})

@login_required
def obtener_producto(request):
    # Obtener el código del producto desde la solicitud (puede ser código o código de barras)
    codigo = request.GET.get('codigo', '').strip()

    if not codigo:
        return JsonResponse({'error': 'Código o código de barras no proporcionado'}, status=400)

    # Buscar producto por código o código de barras
    producto = Producto.objects.filter(codigo=codigo).first() or Producto.objects.filter(codigo_barras=codigo).first()

    if producto:
        # Retornar los detalles del producto
        data = {
            'nombre': producto.nombre,
            'precio': producto.precio_publico,
            'codigo': producto.codigo,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

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
    productos = Producto.objects.all()

    # Agregar producto
    if 'add_product' in request.POST:
        codigo = request.POST.get('codigo')
        codigo_barras = request.POST.get('codigo_barras')
        nombre = request.POST.get('nombre')
        cantidad = request.POST.get('cantidad')
        precio_interno = request.POST.get('precio_interno')
        precio_publico = request.POST.get('precio_publico')

        if all([codigo, codigo_barras, nombre, cantidad, precio_interno, precio_publico]):
            try:
                Producto.objects.create(
                    codigo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
                    cantidad=int(cantidad),
                    precio_interno=float(precio_interno),
                    precio_publico=float(precio_publico),
                )
                messages.success(request, f"Producto '{nombre}' agregado correctamente.")
            except Exception as e:
                messages.error(request, f"Ocurrió un error al agregar el producto: {str(e)}")
        else:
            messages.error(request, "Todos los campos son obligatorios.")

        return redirect('administrar_inventario')

    # Modificar cantidades
    if 'modificar_cantidad' in request.POST:
        producto_id = request.POST.get('producto_id')
        nueva_cantidad = int(request.POST.get('nueva_cantidad'))

        try:
            producto = Producto.objects.get(id=producto_id)
            producto.cantidad = nueva_cantidad
            producto.save()
            messages.success(request, f"Cantidad de '{producto.nombre}' actualizada.")
        except Producto.DoesNotExist:
            messages.error(request, "El producto no existe.")
        return redirect('administrar_inventario')

    # Modificar precios
    if 'modificar_precio' in request.POST:
        producto_id = request.POST.get('producto_id')
        nuevo_precio_interno = float(request.POST.get('nuevo_precio_interno'))
        nuevo_precio_publico = float(request.POST.get('nuevo_precio_publico'))

        try:
            producto = Producto.objects.get(id=producto_id)
            producto.precio_interno = nuevo_precio_interno
            producto.precio_publico = nuevo_precio_publico
            producto.save()
            messages.success(request, f"Precios de '{producto.nombre}' actualizados.")
        except Producto.DoesNotExist:
            messages.error(request, "El producto no existe.")
        return redirect('administrar_inventario')

    # Eliminar producto
    if 'eliminar_producto' in request.POST:
        producto_id = request.POST.get('producto_id')

        try:
            producto = Producto.objects.get(id=producto_id)
            producto.delete()
            messages.success(request, f"Producto '{producto.nombre}' eliminado.")
        except Producto.DoesNotExist:
            messages.error(request, "El producto no existe.")
        return redirect('administrar_inventario')
    
    return render(request, 'administrar_inventario.html', {'productos': productos})

