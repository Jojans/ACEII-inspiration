from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Producto
from django.http import JsonResponse  
from .models import Producto, Venta
import json
from datetime import date
from django.utils import timezone
import logging

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

    # Si se está enviando la caja inicial, la guardamos en la sesión
    if request.method == 'POST':
        if 'set_caja_inicial' in request.POST:
            valor_caja_inicial = request.POST.get('valor_caja_inicial')
            valor_caja_inicial = float(valor_caja_inicial)
            request.session['caja_inicial'] = f"${valor_caja_inicial:,.2f}"
            return redirect('ventas')

        # Si se está agregando un producto, lo guardamos en la sesión
        if 'agregar_producto' in request.POST:
            producto_codigo = request.POST.get('producto_codigo')
            cantidad = int(request.POST.get('cantidad', 1))
            
            producto = Producto.objects.get(codigo=producto_codigo)
            
            # Recuperamos los productos vendidos desde la sesión, si ya hay productos
            productos_vendidos = request.session.get('productos_vendidos', [])
            
            # Agregamos el producto vendido a la lista
            productos_vendidos.append({
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'precio': producto.precio_publico,
                'total': producto.precio_publico * cantidad
            })

            # Guardamos los productos vendidos en la sesión
            request.session['productos_vendidos'] = productos_vendidos

            return redirect('ventas')

    # Obtener el valor de la caja inicial (si existe)
    caja_inicial = request.session.get('caja_inicial', '')
    
    # Obtener los productos vendidos (si existen)
    productos_vendidos = request.session.get('productos_vendidos', [])

    # Convertir la lista de productos vendidos a JSON
    productos_vendidos_json = json.dumps(productos_vendidos)

    return render(request, 'ventas.html', {
        'caja_inicial': caja_inicial,
        'productos': productos,
        'productos_vendidos_json': productos_vendidos_json,  # Pasamos los productos vendidos como JSON
    })

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
    fecha_filtro = request.GET.get('fecha', None)
    
    if fecha_filtro:
        ventas = Venta.objects.filter(fecha=fecha_filtro).order_by('-id')
    else:
        ventas = Venta.objects.all().order_by('-id')
    
    return render(request, 'historial_ventas.html', {'ventas': ventas})

@login_required
def administrar_inventario(request):
    productos = Producto.objects.all()

    # Agregar producto
    if 'add_product' in request.POST:
        codigo = request.POST.get('codigo')
        codigo_barras = request.POST.get('codigo_barras')
        nombre = request.POST.get('nombre')
        precio_interno = request.POST.get('precio_interno')
        precio_publico = request.POST.get('precio_publico')

        if all([codigo, codigo_barras, nombre, precio_interno, precio_publico]):
            try:
                Producto.objects.create(
                    codigo=codigo,
                    codigo_barras=codigo_barras,
                    nombre=nombre,
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

# Crear un logger
logger = logging.getLogger(__name__)

def cerrar_caja(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            caja_inicial = data.get('caja_inicial', 0)
            productos_vendidos = data.get('productos_vendidos', [])

            if caja_inicial is None:
                return JsonResponse({'status': 'error', 'message': 'Caja inicial no proporcionada'}, status=400)

            # Listas para almacenar las informaciones de los productos
            cantidades = []
            precios = []
            productos = []
            totales = []

            # Recorrer los productos vendidos y extraer los datos
            for producto_data in productos_vendidos:
                nombre = producto_data['nombre']
                precio = float(producto_data['precio'])
                cantidad = int(producto_data['cantidad'])
                total_producto = precio * cantidad

                # Agregar los datos a las listas correspondientes
                productos.append(nombre)
                precios.append(f"{precio:.2f}")  # Asegurarse de que el precio tenga dos decimales
                cantidades.append(str(cantidad))
                totales.append(f"{total_producto:.2f}")  # Asegurarse de que el total tenga dos decimales

            # Concatenar las listas en cadenas separadas por comas
            cantidad_str = ",".join(cantidades)
            precio_str = ",".join(precios)
            producto_str = ",".join(productos)
            total_str = ",".join(totales)

            # Crear la venta con los datos obtenidos
            venta = Venta.objects.create(
                fecha=timezone.now().date(),
                caja_inicial=caja_inicial,
                total_dia=0.0,  # Este valor se calculará después
                cantidad=cantidad_str,
                precio=precio_str,
                total_producto=total_str,
                producto=producto_str
            )

            # Calcular el total de los productos vendidos (sumar los totales)
            total_producto = sum(float(total) for total in totales)  # Sumar los totales de los productos vendidos

            # Calcular total_dia (total de productos + caja inicial)
            total_dia = total_producto + caja_inicial

            # Actualizar el total_dia de la venta
            venta.total_dia = total_dia
            venta.save()

            return JsonResponse({'status': 'ok', 'total_dia': venta.total_dia})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def eliminar_venta(request, id):
    # Obtener la venta por ID o mostrar error si no se encuentra
    venta = get_object_or_404(Venta, id=id)
    
    # Eliminar la venta
    venta.delete()
    
    # Redirigir al historial de ventas después de eliminar
    return redirect('historial_ventas')  # Reemplaza 'historial_ventas' por la URL correcta de tu vista de historial

def generar_pdf(request):
    return 0


def generar_excel(request):
    return 0

