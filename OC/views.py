from datetime import datetime
from django.db.models.manager import ManagerDescriptor
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import requests
from OC.models import OrdenDeCompra
from base64 import b64encode, urlsafe_b64encode
from hashlib import sha1
import hmac
import json
from OC.informacion_vacunas import *
from OC.funciones_OC import *
from OC.funciones_vacunas import *

# Parámetros
url_OC = URL_OC_P
url_bodega = URL_BODEGA_P
self_url = 'http://aysen17.ing.puc.cl'
ids_grupos = ids_grupos_produccion
token = TOKEN_P

# url_OC = URL_OC_D
# url_bodega = URL_BODEGA_D
# self_url = 'http://localhost:8000'
# ids_grupos = ids_grupos_desarrollo
# token = TOKEN_D

def get_stocks(request):
    if request.method == 'GET':
        consulta_inicial = 'GET'
        hash_hmac = hmac.new(token.encode(), consulta_inicial.encode(), sha1).digest()
        request_hash = b64encode(hash_hmac).decode('utf-8')
        header_get_almacenes = {
        'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
        'Content-Type': 'application/json',
        'Key': token
        }
        res_almacenes = requests.get(f'{url_bodega}/almacenes', 
        headers=header_get_almacenes)
        lista_almacenes = json.loads(res_almacenes.text)   
        ### recorremos todos los almacenes para buscar stocks
        dict_stocks = dict()
        for almacen in lista_almacenes:
            if not (almacen["recepcion"]) and not(almacen["despacho"]) and not(almacen["pulmon"]):
                consulta_almacen = 'GET{}'.format(almacen['_id'])
                hash_hmac_almacen = hmac.new(token.encode(), consulta_almacen.encode(), sha1).digest()
                request_hash_almacen = b64encode(hash_hmac_almacen).decode('utf-8')
                header_get_almacen = {
                'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash_almacen), 
                'Content-Type': 'application/json',
                'Key': token
                }
                res_almacen = requests.get(
                '{}/skusWithStock?almacenId={}'.format(
                url_bodega, almacen['_id']), headers=header_get_almacen)
                stock_almacen = json.loads(res_almacen.text)       
                for sku in stock_almacen:
                    if sku['_id'] in dict_stocks.keys():
                        dict_stocks[sku['_id']] += sku['total']
                    else:
                        dict_stocks[sku['_id']] = sku['total']
        lista_stock = list()
        for sku in dict_stocks.keys():
            lista_stock.append({'sku': str(sku), 'total': dict_stocks[sku]})
        # escribir('Llamada GET get_stocks')
        return JsonResponse(lista_stock, status=status.HTTP_200_OK, safe=False)
    else:
        respuesta = {
                    'mensaje': 'Not a GET request'
                }
        # escribir('get_stocks se cayó')
        return JsonResponse(respuesta, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'PATCH'])
def recibir_orden(request, orden_id):
    if request.method == 'POST': # Recepción de ordenes de compra
        try:
            print('post try')
            resultado = requests.get(url_OC + '/obtener/'+ orden_id)
            print('1')
            if resultado.status_code == 200 and len(resultado.json())>0: # Si la orden existe en la API
                print('2')
                if not(OrdenDeCompra.objects.filter(_id = orden_id).exists()):
                    print(f'3. data_orden {resultado.json()} orden id: {orden_id}')
                    data_orden = resultado.json()[0]
                    print('4')
                    # Si producimos el ingrediente
                    if int(data_orden['sku']) in ingredientes_nuestros.keys():
                        print('5')
                        stock_almacen = consultar_almacen_general()
                        print('6')
                        # Si tenemos la cantidad pedida en el almacen general, se acepta
                        # Ojo, agregar cantidad en almacen pulmon? Modificar consultar_almacen_general?
                        if data_orden['sku'] in stock_almacen.keys():
                            print('7')
                            if int(data_orden['cantidad']) <= stock_almacen[data_orden['sku']]:
                                print('Orden es aceptada')
                                estado_orden = "aceptada"
                                mensaje = {
                                    "_id": orden_id
                                }
                                requests.post(url_OC + '/recepcionar/'+ orden_id, data= mensaje)
                            else: 
                                print('No tenemos stock')
                                estado_orden = "rechazada"
                                mensaje = {
                                    "rechazo": "No hay stock disponible"
                                }
                                requests.post(url_OC + '/rechazar/'+ orden_id, data = mensaje)
                        else: 
                            print('No tenemos ingrediente actualmente')
                            estado_orden = "rechazada"
                            mensaje = {
                                "rechazo": "No tenemos ingrediente actualmente"
                            }
                            requests.post(url_OC + '/rechazar/'+ orden_id, data = mensaje)
                    else: # Criterio para rechazar
                        print('No producimos ese ingrediente')
                        estado_orden = "rechazada"
                        mensaje = {
                            "rechazo": "No producimos ese ingrediente"
                        }
                        requests.post(url_OC + '/rechazar/'+ orden_id, data = mensaje)
                    respuesta_solicitud = {'estado': estado_orden}
                    print('8')
                    urlNotificacion = url_recepcion_OC['2']
                    print('9')
                    requests.patch(urlNotificacion + '/' + data_orden['_id'], data= respuesta_solicitud)
                    print('10')
                    # Mejor no intentar crear una nueva orden siendo que pueden llegar malas
                    nueva_orden = OrdenDeCompra.objects.create(_id= data_orden['_id'], 
                        cliente = data_orden['cliente'],
                        proveedor = data_orden['proveedor'],
                        sku = data_orden['sku'],
                        fechaEntrega = data_orden['fechaEntrega'],
                        cantidad = data_orden['cantidad'],
                        cantidadDespachada = data_orden['cantidadDespachada'],
                        precioUnitario = data_orden['precioUnitario'],
                        canal = 'b2b',
                        estado = estado_orden,
                        notas = '',
                        rechazo = '',
                        anulacion = '',
                        urlNotificacion = urlNotificacion,
                        created_at = data_orden['created_at'],
                        updated_at = data_orden['updated_at'])
                    respuesta = {
                        'id': nueva_orden._id,
                        'cliente': nueva_orden.cliente,
                        'proveedor' : nueva_orden.proveedor,
                        'sku': nueva_orden.sku,
                        'fechaEntrega': nueva_orden.fechaEntrega,
                        'cantidad': nueva_orden.cantidad,
                        'precioUnitario': nueva_orden.precioUnitario,
                        'canal': nueva_orden.canal,
                        'urlNotificacion': nueva_orden.urlNotificacion,
                        'estado': 'recibida'
                    }
                    print(f'orden creada en la bdd: {nueva_orden}')
                    return Response(respuesta, content_type='application/json', status=status.HTTP_201_CREATED)
                else: # Si ya está creada mando error
                    print('Orden repetida error')
                    respuesta = {
                        'mensaje': 'Orden de Compra ya fue recibida'
                    }
                    return Response(respuesta, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
            else: # NOT FOUND, la orden no existe en la API
                print('Orden pedida no existe en la api')
                respuesta = {
                    'mensaje': 'Error: no existe orden de compras en Sistema de OC'
                }
                return Response(respuesta, content_type='application/json', status=status.HTTP_400_BAD_REQUEST)
        except:
            print('post except')
            respuesta = {
                    'mensaje': 'Ha ocurrido un error inesperado'
                }
            return Response(respuesta, content_type='application/json', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if request.method == 'PATCH': # recibir notificacion de aceptar/rechazar de otro grupo
        try:
            # print('Patch try')
            if OrdenDeCompra.objects.filter(_id = orden_id).exists(): # Si existe en mi base de datos, actualizo estado
                data = request.data
                orden = OrdenDeCompra.objects.filter(_id = orden_id)[0]
                orden.estado = data["estado"]
                orden.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else: # Si no existe en mi base de datos
                return Response(status=status.HTTP_404_NOT_FOUND)
        except:
            print('Patch except 500')
            respuesta = {
                    'mensaje': 'Ha ocurrido un error inesperado'
                }
            return Response(respuesta, content_type='application/json', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print('ordenes not post ni patch 500')
        respuesta = {
                    'mensaje': 'Ha ocurrido un error inesperado'
                }
        return Response(respuesta, content_type='application/json', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def prueba(request):
   if request.method == 'GET':
       #cambiar_stock_almacenes('117', 100)
       enviar_stock_cliente('60caa3af31df040004e88df2', '117', 100, '60f96eced767dc0004a55a7b', 100)
       return Response(status=status.HTTP_200_OK)

# @api_view(['GET'])
# def prueba(request):
#    if request.method == 'GET':
#         print('prueba')
#         return Response(status=status.HTTP_200_OK)

# for orden in OrdenDeCompra.objects.filter(canal = 'ftp').filter(estado = 'recibida'): # or estado = produciendo vacunas or
#     # estado = produciendo ingredientes

#     chequeo si tengo vacunas para mandar a orden
#     if tengo:
#         mandar vacunas a embajada 
#         estado orden = 'lista'
#     if tengo ingredientes para producir vacuna and (estado != produciendo vacunas or estado != produciendo ingredientes):
#         mandar a producir vacunas 
#         estado orden = 'produciendo vacunas'
#     if no tengo ni los ingredientes and estado != produciendo ingredientes:
#         fabricar ingredientes para producir pedido 
#         estado orden = 'produciendo ingredientes'
