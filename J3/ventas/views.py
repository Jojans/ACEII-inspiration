from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Producto
from django.http import JsonResponse  
from .models import Producto, HistorialVenta
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from openpyxl import Workbook
from django.utils import timezone


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
                'cantidad': cantidad,
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
    # Obtener la fecha actual
    today = timezone.now().date()

    # Obtener las ventas realizadas en el día de hoy
    ventas = HistorialVenta.objects.filter(fecha_venta__date=today)  # Filtrar por fecha de venta

    return render(request, 'historial_ventas.html', {'ventas': ventas})


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




@login_required
def cerrar_caja(request):
    if request.method == 'POST':
        # Obtener los productos vendidos desde el formulario
        productos_vendidos_json = request.POST.get('productos_vendidos')

        # Verificar si productos_vendidos_json no está vacío
        if productos_vendidos_json:
            # Convertir el JSON a una lista de productos
            try:
                productos_vendidos = json.loads(productos_vendidos_json)
                
                # Guardar las ventas en HistorialVenta
                for producto_data in productos_vendidos:
                    producto = Producto.objects.get(codigo=producto_data['codigo'])
                    HistorialVenta.objects.create(
                        producto=producto,
                        cantidad=producto_data['cantidad'],
                        precio=producto.precio_publico,
                        total=producto_data['total']
                    )
                
                # Limpiar productos vendidos de la sesión
                request.session['productos_vendidos'] = []
                return redirect('historial_ventas')
            except json.JSONDecodeError:
                # Si ocurre un error con el JSON, puedes manejarlo aquí
                return render(request, 'error.html', {'message': 'Error al procesar los productos vendidos.'})

    return redirect('ventas')

def generar_pdf(request):
    ventas = HistorialVenta.objects.all()  # Obtener todas las ventas
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="historial_ventas.pdf"'

    c = canvas.Canvas(response, pagesize=letter)
    c.drawString(100, 750, "Historial de Ventas")
    y_position = 730

    for venta in ventas:
        c.drawString(100, y_position, f"Producto: {venta.producto.nombre}, Cantidad: {venta.cantidad}, Total: {venta.total}")
        y_position -= 20

    c.save()
    return response


def generar_excel(request):
    ventas = HistorialVenta.objects.all()  # Obtener todas las ventas
    wb = Workbook()
    ws = wb.active
    ws.title = "Ventas"
    ws.append(["Producto", "Cantidad", "Precio", "Total"])

    for venta in ventas:
        ws.append([venta.producto.nombre, venta.cantidad, venta.precio, venta.total])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="historial_ventas.xlsx"'
    wb.save(response)

    return response

