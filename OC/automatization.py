import requests
from OC.models import OrdenDeCompra
from base64 import b64encode, urlsafe_b64encode
from hashlib import sha1
import hmac
import json
from OC.informacion_vacunas import *


#PARAMETROS
#PRODUCCION
url_OC = URL_OC_P
url_bodega = URL_BODEGA_P
self_id = SELF_ID_P
self_url = 'http://aysen17.ing.puc.cl'
ids_grupos = ids_grupos_produccion
token = TOKEN_P
ids_almacen_recepcion = ids_almacen_recepcion_produccion

#DESARROLLO
# url_OC = URL_OC_D
# url_bodega = URL_BODEGA_D
# self_id = SELF_ID_D
# token = TOKEN_D
# ids_grupos = ids_grupos_desarrollo
# ids_almacen_recepcion = ids_almacen_recepcion_desarrollo

def moveStock(id_producto, id_almacen_destino):
    consulta = "POST"+str(id_producto)+str(id_almacen_destino)
    
    hash_hmac = hmac.new(token.encode(), consulta.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')

    header_move_stock = {
      'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash),
    }
    data = {
        'productoId': id_producto,
        'almacenId': id_almacen_destino
    }

    respuesta = requests.post(url_bodega +'/moveStock',
    headers=header_move_stock,
    data=data)

    return respuesta

def moveStockBodega(id_producto, id_almacen, id_oc, precio):
    consulta = "POST"+str(id_producto)+str(id_almacen)

    hash_hmac = hmac.new(token.encode(), consulta.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')

    header_move_stock_bodega = {
      'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash),
    }

    data = {
        'productoId': id_producto,
        'almacenId': id_almacen,
        'oc': id_oc,
        'precio': precio
    }

    respuesta = requests.post(url_bodega + '/moveStockBodega',
    headers=header_move_stock_bodega,
    data=data)

def obtener_almacenes():

    consulta = 'GET'
    hash_hmac = hmac.new(token.encode(), consulta.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')

    header_get_almacenes = {
      'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
      'Content-Type': 'application/json',
      'Key': token
    }

    res_almacenes = requests.get(url_bodega + '/almacenes', 
    headers=header_get_almacenes)
    lista_almacenes = json.loads(res_almacenes.text)
    
    return lista_almacenes

def obtener_productos_almacen(id_almacen, sku):
    consulta = 'GET'+ str(id_almacen) + str(sku)

    hash_hmac = hmac.new(token.encode(), consulta.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')

    header_get_products_by_sku = {
      'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
      'Content-Type': 'application/json',
      'Key': token
    }

    data = {
        'almacenId': id_almacen,
        'sku': sku,
        'limit': 200
    }

    resultado = requests.get(url_bodega + '/stock?almacenId=' + str(id_almacen) + '&sku=' + str(sku),
        headers=header_get_products_by_sku,
        data=data)

    dict_productos = json.loads(resultado.text)
    return dict_productos

def obtener_skus_con_stock(id_almacen):
    consulta = 'GET'+ str(id_almacen)

    hash_hmac = hmac.new(token.encode(), consulta.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')

    header_get_skus_with_stock = {
      'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
      'Content-Type': 'application/json',
      'Key': token
    }

    data = {
        'almacenId': id_almacen
    }

    resultado = requests.get(url_bodega + '/skusWithStock?almacenId='+str(id_almacen),
    headers=header_get_skus_with_stock,
    data=data)

    lista_resultado = json.loads(resultado.text)
    return lista_resultado

