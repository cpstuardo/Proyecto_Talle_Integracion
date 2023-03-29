import requests
from base64 import b64encode, urlsafe_b64encode
from hashlib import sha1
import hmac
from OC.models import OrdenDeCompra
from dashboard.models import Dashboard
import json
from math import floor
from OC.automatization import moveStock, obtener_productos_almacen
from time import sleep
#from OC.informacion_vacunas import ingredientes, ids_almacen_recepcion_desarrollo, ids_grupos_desarrollo, ingredientes_grupos, url_recepcion_OC, ids_almacen_recepcion_produccion, ids_grupos_produccion
from OC.informacion_vacunas import *
from OC.funciones_OC import *

import datetime
from random import choice

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

#DATOS VACUNAS IMPORTADOS
ingredientes_vacuna = INGREDIENTES_VACUNA
lotes_por_vacuna = LOTES_POR_VACUNA
ingredientes = ingredientes_nuestros
##############################################################################################
  
#funcion para calcular el maximo de lotes de vacunas sku que se puede fabricar segun el stock del 
#almacen general
def maximo_lotes_vacuna(sku):  # No se usa
  
  #consultamos si hay stock para la vacuna en el almacen general
  almacenamiento_id = get_almacen_id('general')
  authorization_string = 'GET{}'.format(almacenamiento_id)

  hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
  request_hash = b64encode(hash_hmac).decode('utf-8')

  header_get_stock_almacen = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
    'Content-Type': 'application/json',
    'Key': token
  }

  res_get_stock_almacen = requests.get(
    '{}/skusWithStock?almacenId={}'.format(url_bodega,
      almacenamiento_id), headers=header_get_stock_almacen)

  stock_almacen = json.loads(res_get_stock_almacen.text) ## retorna lista de diccionarios con stock = [{"_id", sku_num, "total": "cantidad"}]

  lista_sku_stock = dict() # elementos son sku: cantidad.. ejem: 10001: 20

  for producto in stock_almacen:
    if producto['_id'] not in lista_sku_stock.keys():
      lista_sku_stock[producto['_id']] = producto['total']

    else:
      lista_sku_stock[producto['_id']] += producto['total']

  ingredientes_por_lote = ingredientes_vacuna[sku] #ideal obtenerlo en una consulta
  cantidad_de_lotes = list()

  for ingrediente in ingredientes_por_lote.keys():
    if ingredientes_por_lote[ingrediente] > 0:
      if ingrediente not in lista_sku_stock.keys():
        return 0
      
      else:
        cantidad_de_lotes.append(
          floor(lista_sku_stock[ingrediente]/ingredientes_por_lote[ingrediente]))

  return min(cantidad_de_lotes)


def moveAllStockAlmacenes(almacen_origen, almacen_destino, stock_almacen):
  for producto in stock_almacen:
    producto_sku = producto['_id']

    authorization_string = 'GET{}{}'.format(almacen_origen, producto_sku)

    hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')

    header_get_stock_almacen = {
      'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
      'Content-Type': 'application/json',
      'Key': token
    }

    res_get_stock_almacen = requests.get(
      '{}/stock?almacenId={}&sku={}'.format(url_bodega, 
        almacen_origen, producto_sku), headers=header_get_stock_almacen)

    stock = json.loads(res_get_stock_almacen.text)

    for elemento in stock:
      a = moveStock(elemento['_id'], almacen_destino)
      sleep(0.8)

#funcion para verificar si hay elementos en el almacen de recepcion y trasladarlo al almacen general
def moveStock_recepcion_to_general(): ## verficado ##
  id_almacen_general = get_almacen_id('general')

  #consultamos si hay stock para la vacuna en el almacen general
  almacenamiento_id = get_almacen_id('recepcion')
  authorization_string = 'GET{}'.format(almacenamiento_id)

  hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
  request_hash = b64encode(hash_hmac).decode('utf-8')

  header_get_stock_almacen = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
    'Content-Type': 'application/json',
    'Key': token
  }

  res_get_stock_almacen = requests.get(
    '{}/skusWithStock?almacenId={}'.format(url_bodega, 
      almacenamiento_id), headers=header_get_stock_almacen)

  stock_almacen = json.loads(res_get_stock_almacen.text)
  # escribir(f"Stock almacen = {stock_almacen}")
  if len(stock_almacen) > 0:
    #ejecutar codigo/funcion para trasladar a almacen general
    moveAllStockAlmacenes(almacenamiento_id, id_almacen_general, stock_almacen)
  # escribir("Terminó funcion")


#funcion retorna una lista de diccionarios con los ingredientes restantes para producir la cantidad
#de lotes de vacunas consultada
def get_ingredientes_restantes(sku, cantidad_de_lotes):
  #consultamos si hay stock para la vacuna en el almacen general
  almacenamiento_id = get_almacen_id('general')
  authorization_string = 'GET{}'.format(almacenamiento_id)

  hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
  request_hash = b64encode(hash_hmac).decode('utf-8')

  header_get_stock_almacen = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
    'Content-Type': 'application/json',
    'Key': token
  }

  res_get_stock_almacen = requests.get(
    '{}/skusWithStock?almacenId={}'.format(url_bodega, 
      almacenamiento_id), headers=header_get_stock_almacen)

  stock_almacen = json.loads(res_get_stock_almacen.text)

  lista_sku_stock = dict() # elementos son sku: cantidad.. ejem: 10001: 20

  for producto in stock_almacen:
    if producto['_id'] not in lista_sku_stock.keys():
      lista_sku_stock[producto['_id']] = producto['total']

    else:
      lista_sku_stock[producto['_id']] += producto['total']

  ingredientes_por_lote = ingredientes_vacuna[sku] #ideal obtenerlo en una consulta
  ingredientes_restantes = dict()
  
  for ingrediente in ingredientes_por_lote.keys():
    if ingredientes_por_lote[ingrediente] > 0:
      if ingrediente in lista_sku_stock.keys():
        diferencia = lista_sku_stock[ingrediente] - ingredientes_por_lote[ingrediente]*cantidad_de_lotes
        if diferencia < 0:
          ingredientes_restantes[ingrediente] = diferencia*(-1)

      else:
        ingredientes_restantes[ingrediente] = ingredientes_por_lote[ingrediente]*cantidad_de_lotes

  return ingredientes_restantes

##mover cantidad determinada de productos de un cierto sku entre almacenes
def moveStock_cantidad(almacen_origen, almacen_destino, sku, cantidad):
  authorization_string = 'GET{}{}'.format(almacen_origen, sku)

  hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
  request_hash = b64encode(hash_hmac).decode('utf-8')

  header_get_stock_almacen = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
    'Content-Type': 'application/json',
    'Key': token
  }

  res_get_stock_almacen = requests.get(
    '{}/stock?almacenId={}&sku={}'.format(url_bodega, 
      almacen_origen, sku), headers=header_get_stock_almacen)

  stock = json.loads(res_get_stock_almacen.text)
  
  cantidad_restante = len(stock)

  for i in range(0, cantidad):
    if cantidad_restante > 0:
      moveStock(stock[i]['_id'], almacen_destino)
      sleep(0.8)
      cantidad_restante -= 1

def fabricar_vacunas(sku, cantidad_lotes):

  ### codigo/funcion para trasladar desde almacen general a despacho
  general_id = get_almacen_id('general')
  despacho_id = get_almacen_id('despacho')

  for ingrediente in ingredientes_vacuna[sku].keys():
    moveStock_cantidad(general_id, despacho_id, 
    ingrediente, cantidad_lotes*ingredientes_vacuna[sku][ingrediente])
  escribir('Ingrediente enviado a despacho')
  ## mandar a fabricar
  cantidad_por_lote = lotes_por_vacuna[sku]
  authorization_string = 'PUT{}{}'.format(sku, cantidad_lotes*cantidad_por_lote)

  hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
  request_hash = b64encode(hash_hmac).decode('utf-8')

  header_fabricar_vacunas = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
  }

  cantidad = cantidad_por_lote*cantidad_lotes
  body = {
    "sku": sku,
    "cantidad": cantidad
  }

  res_fabricar_vacunas = requests.put(
    '{}/fabrica/fabricarSinPago'.format(url_bodega), 
  headers=header_fabricar_vacunas, data=body)

  ## ver si se guarda o no el datalle de fabricar vacunas/ingredientes
  detalle_fabricar_vacunas = json.loads(res_fabricar_vacunas.text)
  escribir('vacuna enviada a fabricar')
  #Llevar registro de la cantidad de vacunas que han sido fabricadas en bd y asi
  # mostrarlas en el dashboard
  if len(Dashboard.objects.all()) == 0:
    d = Dashboard()
    d.save()
  dashboard = Dashboard.objects.all()[0]
  dashboard.vacunas_fabricadas += cantidad
  dashboard.save()
  escribir('Vacuna registrada')
  return detalle_fabricar_vacunas

#funcion para mandar a producir y pedir sku faltantes para vacuna
def fabricar_pedir(sku, cantidad_de_lotes):
  ingredientes_restantes = get_ingredientes_restantes(sku, cantidad_de_lotes)
  for ingrediente in ingredientes_restantes.keys():
    if int(ingrediente) in ingredientes.keys():
      lote = ingredientes[int(ingrediente)]['lote']
      por_pedir = ingredientes_restantes[ingrediente]

      lotes_por_pedir = floor(por_pedir/lote) + 1

      fabricar_ingredientes(ingrediente, lotes_por_pedir*lote)

    else:
      ## ejecutar codigo para mandar a pedir a otro grupo
      lote = ingredientes_grupos[int(ingrediente)]['lote']
      por_pedir = ingredientes_restantes[ingrediente]

      lotes_por_pedir = floor(por_pedir/lote) + 1
      
      pedir_grupos(ingrediente, lotes_por_pedir*lote)
        


######################################### 

#FUNCION QUE SE LLAMA EN MAIN PARA VERIFICAR, MOVER Y DESPACHAR VACUNAS
def mover_y_despachar_vacunas():
  #Paso 1: rescatar las vacunas en general
  vacunas_para_despachar = get_vacunas_general()
  #Paso 2: mover y despachar a destino
  mover_vacunas_general_a_despacho(vacunas_para_despachar)

  #paso 3:
  #iterar en las vacunas a despachar
  #   vacuna: ir satisfaciendo las ordens de compra de embajadas que van a estar ne la bd
  #   e ir disminuyendo su atributo "cantidad" hasta llegar a cero.
  #   priorizando segun, antiguedad de la orden y tipo de sku pedido. 
  

# Endpoint despachar vacuna a la embajada
def despachar_vacuna(productoId, oc, direccion, precio):
  consulta = "DEL"+"ETE"+str(productoId)+str(direccion) + str(precio) + str(oc)
  
  hash_hmac = hmac.new(token.encode(), consulta.encode(), sha1).digest()
  request_hash = b64encode(hash_hmac).decode('utf-8')

  header_despachar_vacuna = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash),
    'Content-Type': 'application/json',
  }

  data = {
      'productoId': productoId,
      'oc': oc,
      'direccion': direccion,
      'precio': precio
  }

  respuesta = requests.delete(url_bodega +'/stock',
  headers=header_despachar_vacuna,
  data=data)
  sleep(0.8)

  return respuesta

# Se obtiene diccionario de vacunas disponibles para poder despachar, pero que están en general
def get_vacunas_general():
  #print(f"get vacunas general")
  almacen_id = get_almacen_id('general')
  #Obtener vacunas
  vacunas = dict()
  for sku in SKU_VACUNAS:      
    authorization_string = 'GET{}{}'.format(almacen_id, sku)

    hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')

    header_get_stock_almacen = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash)
    }
    res_get_stock_almacen = requests.get(
      f'{url_bodega}/stock?almacenId={almacen_id}&sku={sku}&limit=200',
      headers=header_get_stock_almacen)
    stock_almacen = res_get_stock_almacen.json()
    
    vacunas[str(sku)] = stock_almacen

  return vacunas

# Mover Vacunas de almacen general a despacho y despachar
def mover_vacunas_general_a_despacho(vacunas):
  #print(f"mover vacunas a despacho y despachar")
  keys_vacunas = vacunas.keys()

  #print(f"Keys vacunas: {keys_vacunas}")
  #Recorro cada sku de vacunas
  for key in keys_vacunas:
    #Hay vacunas de ese SKU, entonces las muevo
    #print(f"key: {key} | vacunas[key]: {vacunas[key]}")

    if len(vacunas[key]) > 0:
      id_almacen_origen = get_almacen_id('general')
      id_almacen_destino = get_almacen_id('despacho')
      moveStock_cantidad(id_almacen_origen, id_almacen_destino, key, len(vacunas[key]))
      
      #Despues de mover, despachamos
      direccion = 'embajada' #HARCODED
      precio = 10 #HARCODED

      #Recorro cada vacuna para un sku
      for vacuna in vacunas[key]:
        oc_a_cumplir = get_OC_embajada_a_cumplir(key)
        #Si es que hay orden de compra, podemos despachar
        if oc_a_cumplir is not None:
          ocId = oc_a_cumplir._id
          productoId = vacuna['_id']

          respuesta = despachar_vacuna(productoId, ocId, direccion, precio)
          #Si se pudo despachar de forma correcta, se actualizan los datos en la BD
          if respuesta.status_code == 200:
                print(f"Despachado bien")
                #-> Modificar valor en la bd CantidadDespachada += 1
                oc_a_cumplir.cantidadDespachada+= 1
                oc_a_cumplir.save()
                #-> Si es que CantidadDespachada == cantidad pedida:
                if oc_a_cumplir.cantidadDespachada == oc_a_cumplir.cantidad:
                  #-> Cambiar estado a 'finalizada' (De esta forma )
                  oc_a_cumplir.estado = 'finalizada'
                  oc_a_cumplir.save()

                
                

def get_OC_embajada_a_cumplir(sku):
  #Filtro por oc de embajadas, que se encuentren aceptadas (no completadas) y del sku de la vacuna.
  if OrdenDeCompra.objects.filter(canal = "ftp").filter(estado = 'aceptada').filter(sku = sku).exists():
    OC_de_embajadas = OrdenDeCompra.objects.filter(canal = "ftp").filter(estado = 'aceptada').filter(sku = sku)
    #print(f"OC de embajadas: {OC_de_embajadas}")}

    #OC_de_embajadas_ver = [
    #  [elem.cliente, elem.canal, elem.sku,
    #   elem.estado, elem.cantidad, elem.cantidadDespachada,
    #  ] for elem in OC_de_embajadas]
  
    #print(f"ver OC de embajadas a despachar (atributos sin orden) : {OC_de_embajadas_ver}")
    #print("---------------------------------------------------------")
    OC_de_embajadas_ordenadas = sorted(OC_de_embajadas, key = lambda x: x.created_at)

    #OC_de_embajadas_ver = [[elem.created_at,] for elem in OC_de_embajadas_ordenadas]
    #print(f"ver OC de embajadas a despachar ordenadas de menor a mayor (en fecha de creacion): {OC_de_embajadas_ver}")
    OC_embajada_mas_antigua = OC_de_embajadas_ordenadas[0]

    #print(f"Oc embajada mas antigua: {OC_embajada_mas_antigua} | {OC_embajada_mas_antigua.created_at}")
    return OC_embajada_mas_antigua
  return None




def chequear_ingredientes_vacunas(sku, cantidad_de_lotes):
  ingredientes_restantes = get_ingredientes_restantes(sku, cantidad_de_lotes)

  if len(ingredientes_restantes.keys()) == 0:
    return True

  return False


def proceso_vacunas(sku, cantidad_de_lotes, orden):

  chequeo = chequear_ingredientes_vacunas(sku, cantidad_de_lotes)
  if chequeo:
    if orden.notas != 'produciendo_vacunas':
      escribir('fabricar_vacunas')
      fabricar_vacunas(sku, cantidad_de_lotes)
      orden.notas = 'produciendo_vacunas'
      orden.save()

  else:
    if orden.notas != 'produciendo_ingredientes':
      escribir('fabricar ingredientes vacuna faltantes')
      fabricar_pedir(sku, cantidad_de_lotes)
      orden.notas = 'produciendo_ingredientes'
      orden.save()



def mover_pulmon_general(sku, cantidad):
  pulmon_id = get_almacen_id('pulmon')
  recepcion_id = get_almacen_id('recepcion')
  general_id = get_almacen_id('general')

  
  authorization_string = 'GET{}{}'.format(pulmon_id, sku)

  hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
  request_hash = b64encode(hash_hmac).decode('utf-8')

  header_get_stock_almacen = {
    'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
    'Content-Type': 'application/json',
    'Key': token
  }

  res_get_stock_almacen = requests.get(
    '{}/stock?almacenId={}&sku={}'.format(url_bodega, 
      pulmon_id, sku), headers=header_get_stock_almacen)

  stock = json.loads(res_get_stock_almacen.text)

  cantidad_restante = len(stock)

  for i in range(0, cantidad):
    if cantidad_restante > 0:
      producto_id = stock[i]['_id']
      moveStock(producto_id, recepcion_id)
      sleep(0.6)
      moveStock(producto_id, general_id)
      sleep(0.6)
      cantidad_restante -= 1

def chequear_ordenes_vacuna():
  escribir('chequear_ordenes_vacuna')

  ##mover y despachar todas las vacunas ya listas
  mover_y_despachar_vacunas()

  ordenes_embajadas = OrdenDeCompra.objects.filter(
    canal='ftp',
    estado='aceptada'
  )

  for orden in ordenes_embajadas:

    #calcular cantidad de lotes
    cantidad_de_lotes = floor(orden.cantidad/lotes_por_vacuna[str(orden.sku)]) + 1
    proceso_vacunas(str(orden.sku), cantidad_de_lotes, orden)

def restock_grupos():
  escribir('restockeo de grupos')
  sku_grupos = ingredientes_grupos.keys()

  for sku in sku_grupos:
    tiempo_produccion = ingredientes_grupos[sku]['tiempo_produccion']
    stock_almacen = consultar_almacen_general() # {'sku': cantidad}
    if str(sku) not in stock_almacen or stock_almacen[str(sku)]<40:
      escribir(f'mandando a pedir {sku}')
      if tiempo_produccion <= 20:
        cantidad = 4
      elif tiempo_produccion <= 40:
        cantidad = 4
      elif tiempo_produccion <= 50:
        cantidad = 5
      else:
        cantidad = 6

      pedir_grupos(str(sku), cantidad)

    else:
      escribir(f'No se mandó a pedir {sku}')