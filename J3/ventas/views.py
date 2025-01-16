from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor, Product, Compra, Venta
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from decimal import Decimal
from django.contrib import messages
import requests # type: ignore
import csv
from django.conf import settings
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import json

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirigir a la vista de lobby después de un login exitoso
            return redirect('lobby')
        else:
            # Si las credenciales son incorrectas, mostrar un mensaje de error
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')

    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

@login_required
def perfil_usuario(request):
    return render(request, 'perfil.html', {
        'user': request.user
    })

@login_required
def lobby(request):
    if request.user.is_superuser:
        return render(request, 'superuser_dashboard.html')
    else:
        return render(request, 'usuario_dashboard.html')

@login_required
def administrar_sistema(request):
    return render(request, 'administrar_sistema.html')

@login_required
def ventas(request):
    return render(request, 'ventas.html')










@login_required
#inventario
def product_list(request):
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
    products = response.json()

    # Guardar o actualizar productos sin sobrescribir el stock
    for product_data in products:
        # Verificar si el producto ya existe en la base de datos
        producto, created = Product.objects.update_or_create(
            id=product_data['id'],  # Usamos el ID para identificar el producto
            defaults={
                'title': product_data['title'],
                'price': product_data['price'],
                'description': product_data['description'],
                'category': product_data['category'],
                'image': product_data['image'],
                'rating': product_data['rating']['rate'],
            }
        )
        # Aquí no tocamos el campo de stock, por lo que se conserva lo que has asignado

    # Filtrar productos con ID específicos
    productos_filtrados = Product.objects.filter(id__in=[9, 10, 11, 12, 13, 14])

    return render(request, 'product_list.html', {'products': productos_filtrados})

@login_required
#productos
def productos(request):
    # Obtener todos los productos
    productos = Product.objects.all()
    return render(request, 'product_list.html', {'productos': productos})

@login_required
#actualizar stock del producto
def actualizar_stock(request, producto_id):
    # Obtener el producto por su ID
    producto = get_object_or_404(Product, id=producto_id)

    if request.method == 'POST':
        # Obtener el nuevo valor de stock del formulario
        nuevo_stock = int(request.POST.get('stock', 0))

        # Actualizar el stock del producto
        producto.stock = nuevo_stock
        producto.save()  # Guardar el nuevo valor en la base de datos

        # Redirigir a la lista de productos después de la actualización
        return redirect('product_list')  # O la vista que deseas

    # Si no es un POST, renderiza un formulario para actualizar el stock
    return render(request, 'actualizar_stock.html', {'producto': producto})

@login_required
#compras
def compras(request):
    productos = Product.objects.filter(id__in=[9, 10, 11, 12, 13, 14])  # Productos a comprar
    proveedores = Proveedor.objects.all()  # Obtener todos los proveedores

    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor')
        proveedor = Proveedor.objects.get(id=proveedor_id) if proveedor_id else None
        
        # Recoger las cantidades solicitadas para cada producto
        productos_a_comprar = []
        total_compra = 0
        for producto in productos:
            cantidad_pedida = int(request.POST.get(f'cantidad_{producto.id}', 0))

            if cantidad_pedida > 0:
                total_producto = producto.price * cantidad_pedida
                productos_a_comprar.append({
                    'producto': producto,
                    'cantidad': cantidad_pedida,
                    'precio': producto.price,
                    'stock': producto.stock,  # Mostrar stock actual
                    'total': total_producto
                })
                total_compra += total_producto

        # Verificar si se seleccionaron productos
        if not productos_a_comprar:
            return render(request, 'compras.html', {
                'productos': productos,
                'proveedores': proveedores,
                'error': 'Debe seleccionar al menos un producto con cantidad mayor a 0.'
            })

        # Pasar los productos a la plantilla de la factura
        return render(request, 'factura_compra.html', {
            'factura': productos_a_comprar,
            'total_compra': total_compra,
            'proveedor': proveedor
        })

    return render(request, 'compras.html', {
        'productos': productos,
        'proveedores': proveedores
    })

@login_required
#cancelar compra
def cancelar_compra(request):
    # Redirigir a la página de compras sin hacer nada con el stock
    return redirect('compras')  # Redirige a la página de compras

@login_required
#pago contraentrega
def simular_pago(request):
    if request.method == 'POST':
        productos_a_comprar = []
        total_compra = 0
        
        # Recoger los productos seleccionados y sus cantidades
        for producto in Product.objects.filter(id__in=[9, 10, 11, 12, 13, 14]):
            cantidad = int(request.POST.get(f'cantidad_{producto.id}', 0))
            if cantidad > 0:
                total_producto = producto.price * cantidad
                productos_a_comprar.append({
                    'producto': producto,  # Asegúrate de pasar el producto completo
                    'cantidad': cantidad,
                    'precio': producto.price,
                    'total': total_producto
                })
                total_compra += total_producto

        if not productos_a_comprar:
            return redirect('compras')  # Si no se ha seleccionado ningún producto, redirigimos a compras

        # Pasar los productos a la plantilla de factura
        return render(request, 'factura_compra.html', {
            'factura': productos_a_comprar,
            'total_compra': total_compra,
        })

    return redirect('compras')  # Si no es un POST, redirigimos a compras

@login_required
#actualizar_stock
def actualizar_stock(request):
    if request.method == 'POST':
        # Recoger los productos seleccionados y sus cantidades
        productos = request.POST.getlist('productos')  # Lista de productos seleccionados
        cantidades = request.POST.getlist('cantidades')  # Cantidades de productos seleccionados
        
        # Actualizar el stock
        for producto_id, cantidad in zip(productos, cantidades):
            producto = Product.objects.get(id=producto_id)
            producto.stock += int(cantidad)  # Restar las cantidades de stock
            producto.save()

        # Redirigir a la vista de compras después de actualizar el stock
        return redirect('compras')

    # Si no es un POST, redirigir a compras (aunque no debería llegar aquí)
    return redirect('compras')

@login_required
#pago pse
def pagar_pse(request):
    # Simulando la redirección a la página de PSE para fines educativos
    # Aquí se simula la URL de pago, puedes ajustarla según tus necesidades
    pse_url = 'https://www.pse.com.co/persona'  # URL simulada de PSE

    return redirect(pse_url)  # Redirigir al usuario al sitio de PSE

@login_required
#ventas
def ventas(request):
    if request.method == 'POST':
        productos_vendidos = []
        total_venta = Decimal('0.00')
        cantidades = []

        # Recoger los productos seleccionados y sus cantidades
        for producto in Product.objects.filter(id__in=[9, 10, 11, 12, 13, 14]):
            cantidad = int(request.POST.get(f'cantidad_{producto.id}', 0))

            if cantidad > 0:
                producto.stock -= cantidad  # Actualizar stock
                producto.save()

                total = producto.price * cantidad

                productos_vendidos.append({
                    'producto': producto.title,
                    'cantidad': cantidad,
                    'precio': float(producto.price),
                    'total': float(total) 
                })
                total_venta += total # Agregar el total de la venta

        # Verifica que se haya seleccionado al menos un producto
        if not productos_vendidos:
            return render(request, 'ventas.html', {'productos': Product.objects.filter(id__in=[9, 10, 11, 12, 13, 14]), 'error': 'Debe seleccionar al menos un producto con cantidad mayor a 0.'})

        # Guardar datos en la sesión para el CSV
        request.session['factura'] = productos_vendidos
        
        # Redirigir a la página de factura con los productos vendidos
        return render(request, 'factura.html', {
            'factura': productos_vendidos,
            'total_factura': float(total_venta)
            })

    # Obtener los productos a mostrar
    productos = Product.objects.filter(id__in=[9, 10, 11, 12, 13, 14])
    return render(request, 'ventas.html', {'productos': productos})

@login_required
#factura
def generar_factura(request):
    # Recuperar los datos de la factura desde la vista anterior
    factura = request.GET.get('factura', None)

    return render(request, 'factura.html', {
        'factura': factura})

@login_required
#descargar factura
def descargar_factura_csv(request):
    factura = request.session.get('factura', [])
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="factura.csv"'

    # Crear el escritor de CSV con delimitador estándar (coma)
    writer = csv.writer(response)

    # Encabezados del CSV
    writer.writerow(['Producto', 'Cantidad', 'Precio Unitario', 'Total'])

    # Agregar datos de la factura
    for item in factura:
        writer.writerow([item['producto'], item['cantidad'], item['precio'], item['total']])

    return response

@login_required
#guardar proveedores
def importar_proveedores():
    url = "https://randomuser.me/api/?results=10&nat=us"
    response = requests.get(url)
    data = response.json()

    # Limpia la base de datos de proveedores antiguos
    Proveedor.objects.all().delete()

    # Guarda los nuevos proveedores
    for item in data['results']:
        Proveedor.objects.create(
            first_name=item['name']['first'],
            last_name=item['name']['last'],
            address=f"{item['location']['street']['name']} {item['location']['street']['number']}",
            city=item['location']['city'],
            country=item['location']['country'],
            phone=item['phone'],
            email=item['email'],
            picture=item['picture']['medium']
        )

@login_required
def proveedores(request):
    # Importar proveedores solo si no están en la base de datos
    if not Proveedor.objects.exists():
        importar_proveedores()

    proveedores = Proveedor.objects.all()

    return render(request, 'proveedores.html', {'proveedores': proveedores})



