import requests
from base64 import b64encode, urlsafe_b64encode
from hashlib import sha1
import hmac
from OC.models import Contador, OrdenDeCompra
from requests.models import RequestField
import json
from math import floor
from time import sleep
from OC.informacion_vacunas import *
from datetime import *
from random import choice
import random
import paramiko 
import xml.etree.ElementTree as ET
import os
from datetime import datetime


#PARAMETROS
#PRODUCCION
url_OC = URL_OC_P
url_bodega = URL_BODEGA_P
self_id = SELF_ID_P
self_url = 'http://aysen17.ing.puc.cl'
ids_grupos = ids_grupos_produccion
ids_almacen_recepcion = ids_almacen_recepcion_produccion
token = TOKEN_P
password_FTP = PASS_FTP_P
user_FTP = USER_FTP_P

#DESARROLLO
# url_OC = URL_OC_D
# url_bodega = URL_BODEGA_D
# self_id = SELF_ID_D
# token = TOKEN_D
# ids_grupos = ids_grupos_desarrollo
# ids_almacen_recepcion = ids_almacen_recepcion_desarrollo
# password_FTP = PASS_FTP_D
# user_FTP = USER_FTP_D

# Función para completar ordenes de compra
def revisar_stock_OC():
    try:
        print('Inicia revisar stock OC')
        ordenes_aceptadas = OrdenDeCompra.objects.filter(estado = 'aceptada', proveedor = self_id, canal = 'b2b')
        print(f'Ordenes_aceptadas = {ordenes_aceptadas}')
        stock_almacen = consultar_almacen_general()
        print(f'stock_almacen = {stock_almacen}')
        for orden in ordenes_aceptadas:
            print(f'orden {orden}')
            # Si hay stock en el almacen general
            if str(orden.sku) in stock_almacen.keys():
                print(f'orden.sku {orden.sku}')
                print(f'primero {stock_almacen[str(orden.sku)]} tipo {type(stock_almacen[str(orden.sku)])}')
                print(f'segundo {orden.cantidad} tipo {type(orden.cantidad)}')
                if int(stock_almacen[str(orden.sku)]) < int(orden.cantidad): # Si hay stock, pero no el suficiente
                    print(f'cantidad almacen {stock_almacen[str(orden.sku)]}')
                    if not(orden.en_produccion):
                        print(f'Se manda a fabricar ingrediente {orden.sku}')
                        cantidad_a_fabricar = calcular_cantidad_fabricar(orden.sku, orden.cantidad - stock_almacen[str(orden.sku)])
                        fabricar_ingredientes(orden.sku, cantidad_a_fabricar)
                        orden.en_produccion = True
                        orden.save()
                else: # Si hay stock suficiente
                    # Cambiar stock a almacen de despacho 
                    cambiar_stock_almacenes(str(orden.sku), orden.cantidad)
                    # Enviar al otro grupo 
                    enviar_stock_cliente(orden.cliente, orden.sku, orden.cantidad, orden._id, orden.precioUnitario)
                    # Cambiar orden a 'completada'
                    orden.estado = 'completada'
                    orden.save()
                print('if else catch')
            else: # Si no hay nada de stock en el almacen general
                print(f'else catch')
                if not(orden.en_produccion):
                    print(f'No hay nada, se manda a fabricar ingrediente {orden.sku}')
                    cantidad_a_fabricar = calcular_cantidad_fabricar(orden.sku, orden.cantidad)
                    fabricar_ingredientes(orden.sku, cantidad_a_fabricar)
                    orden.en_produccion = True
                    orden.save()
        # escribir('Termina revisar stock OC')
    
    except:
        escribir('Falló funcion')

# Función para obtener el id de un almacén
def get_almacen_id(almacen_buscado):
    consulta_inicial = 'GET'
    hash_hmac = hmac.new(token.encode(), consulta_inicial.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')
    header_get_almacenes = {
        'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
        'Content-Type': 'application/json',
        'Key': token
    }

    res_almacenes = requests.get(f'{url_bodega}/almacenes', headers=header_get_almacenes)
    lista_almacenes = json.loads(res_almacenes.text)
    id_almacen = None
    for almacen in lista_almacenes:
        if almacen_buscado == 'recepcion':
            if almacen['recepcion']:
                id_almacen = almacen['_id']
                break

        elif almacen_buscado == 'despacho':
            if almacen['despacho']:
                id_almacen = almacen['_id']
                break
        
        elif almacen_buscado == 'pulmon':
            if almacen['pulmon']:
                id_almacen = almacen['_id']
                break

        elif almacen_buscado == 'general':
            if not almacen['recepcion'] and not almacen['despacho'] and not almacen['pulmon']:
                id_almacen = almacen['_id']
                break
    return id_almacen      
  
# Función para consultar todo el stock disponible en el almacen general
def consultar_almacen_general():
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
    stock_almacen = res_get_stock_almacen.json()
    lista_sku_stock = dict()
    for producto in stock_almacen:
        if producto['_id'] not in lista_sku_stock.keys():
            lista_sku_stock[producto['_id']] = producto['total']

        else:
            lista_sku_stock[producto['_id']] += producto['total']
    return lista_sku_stock

# Función para mover desde almacen general a despacho
def cambiar_stock_almacenes(sku, cantidad):
    # Obtener productos id a partir de sku
    almacen_id = get_almacen_id('general')
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
    # Mover al almacen de destino
    almacen_destino = get_almacen_id('despacho')
    for i in range(cantidad):
        print(i)
        authorization_string = 'POST{}{}'.format(stock_almacen[i]['_id'], almacen_destino)
        hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
        request_hash = b64encode(hash_hmac).decode('utf-8')
        header = {
            'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash)
        }

        body = {
            'productoId': stock_almacen[i]['_id'],
            'almacenId': almacen_destino
        }
        
        res_move_stock = requests.post(
        url_bodega + '/moveStock',
        headers=header, data = body)
        sleep(0.8)

# Función para enviar el stock a la bodega del cliente
def enviar_stock_cliente(id_cliente, sku, cantidad_enviar, id_oc, precio): 
    # Obtener productos id a partir de sku
    almacen_id = get_almacen_id('despacho')
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
    # Mover stock entre bodegas
    almacen_destino = ids_almacen_recepcion[ids_grupos[id_cliente]]
    for i in range(cantidad_enviar):
        print(f"envié {i}")
        authorization_string = 'POST{}{}'.format(stock_almacen[i]['_id'], almacen_destino)
        hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
        request_hash = b64encode(hash_hmac).decode('utf-8')

        header = {
            'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash)
        }

        body = {
            'productoId': stock_almacen[i]['_id'],
            'almacenId': almacen_destino,
            'oc': id_oc,
            'precio': precio
        }
        res_move_stock = requests.post(
        url_bodega + '/moveStockBodega',
        headers=header, data = body)
        detalle_cambio_stock = json.loads(res_move_stock.text)
        # print(detalle_cambio_stock)
        sleep(0.8)

# Función para calcular la cantidad a fabricar para completar un lote
def calcular_cantidad_fabricar(sku, cantidad_solicitada):
    if cantidad_solicitada % ingredientes_nuestros[sku]['lote'] == 0:
        return cantidad_solicitada
    else:
        resto = cantidad_solicitada % ingredientes_nuestros[sku]['lote']
        return cantidad_solicitada + (ingredientes_nuestros[sku]['lote'] - resto)

# Función para fabricar los ingredientes que faltan para las órdenes
def fabricar_ingredientes(sku, cantidad):
    authorization_string = 'PUT{}{}'.format(sku, cantidad)
    hash_hmac = hmac.new(token.encode(), authorization_string.encode(), sha1).digest()
    request_hash = b64encode(hash_hmac).decode('utf-8')
    header_fabricar_ingredientes = {
        'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash)
    }
    body = {
        "sku": sku,
        "cantidad": cantidad
    }
    res_fabricar_ingredientes = requests.put(
        f'{url_bodega}/fabrica/fabricarSinPago', 
        headers=header_fabricar_ingredientes, data=body)
    detalle_fabricar_ingredientes = json.loads(res_fabricar_ingredientes.text)
    return detalle_fabricar_ingredientes

# Función para mandar a pedir lo que falte
def pedir_grupos(sku, cantidad):
    try:
        grupo_pedir = '20'
        print(f'pido al grupo {grupo_pedir}')
        id_proveedor = encontrar_id(grupo_pedir)
        id_orden = crear_OC(id_proveedor, sku, cantidad)
        print(f'orden id {id_orden}')
        if id_orden != 0:
            envio = enviar_OC(id_orden, id_proveedor)
            if envio:
                return 1
            else:
                return 0
        return 0
    except:
        return 0

# Función para obtener grupo con sku disponible
def grupo_sku_disponible(sku, cantidad):
    lista_grupos_productores = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    grupos_disponible = []
    for grupo in lista_grupos_productores:
        try:
            try:
                resultado_consulta_stock = requests.get(URL_OBTENER_STOCK_GRUPOS[str(grupo)], timeout=5)
            except: 
                pass
            if resultado_consulta_stock.status_code == 200:
                list_sku = resultado_consulta_stock.json()
                for elemento in list_sku:
                    if elemento['sku'] == str(sku):
                        if elemento['total'] >= cantidad:
                            grupos_disponible.append(grupo)
        except:
            pass
    grupo_pedir = random.choice(grupos_disponible)
    return grupo_pedir

# Función para transformar fecha en Javascript Date
def time_millis(date):
    mili_sec = date.timestamp() * 1000
    return mili_sec

# Función para encontrar el id de un grupo a partir de su número
def encontrar_id(grupo):
    for id in ids_grupos.keys():
        if ids_grupos[id] == str(grupo):
            return id

# Función para crear ordenes de compra de lo que necesitemos en el Sistema de Órdenes
def crear_OC(id_grupo_proveedor, sku, cantidad):
    data = {
        "cliente": self_id,
        "proveedor": id_grupo_proveedor,
        "sku": sku,
        "fechaEntrega": time_millis(datetime.now() + timedelta(hours=5)),
        "cantidad": cantidad,
        "precioUnitario": 1,
        "canal": "b2b",
        "urlNotificacion": url_recepcion_OC['17'],
    }
    resultado_creacion = requests.put(url_OC + '/crear', data=data)
    if resultado_creacion.status_code == 200: 
        data_orden = resultado_creacion.json()
        nueva_orden = OrdenDeCompra.objects.create(_id= data_orden['_id'], 
            cliente = self_id,
            proveedor = id_grupo_proveedor, 
            sku = sku,
            fechaEntrega = data_orden['fechaEntrega'],
            cantidad = cantidad,
            cantidadDespachada = data_orden['cantidadDespachada'],
            precioUnitario = data_orden['precioUnitario'],
            canal = data_orden['canal'],
            estado = data_orden['estado'],
            notas = '',
            rechazo = '',
            anulacion = '',
            urlNotificacion = url_recepcion_OC['17'],
            created_at = data_orden['created_at'],
            updated_at = data_orden['updated_at'])
        return data_orden['_id'] # Si se crea bien retorna el id
    return 0 # Si no se crea retorna cero

# Función para enviar la OC al grupo
def enviar_OC(id_orden, id_grupo_proveedor):
    resultado_consulta = requests.get(url_OC + '/obtener/'+ id_orden)
    data_orden = resultado_consulta.json()[0]
    fecha_entrega = datetime.strptime(data_orden['fechaEntrega'], "%Y-%m-%dT%H:%M:%S.%fZ")
    data = {
        "cliente": data_orden['cliente'],
        "sku": data_orden['sku'],
        "fechaEntrega": time_millis(fecha_entrega),
        "cantidad": data_orden['cantidad'],
        "urlNotificacion": data_orden['urlNotificacion']
    }
    url_grupo = url_recepcion_OC[ids_grupos[id_grupo_proveedor]]
    resultado_envio = requests.post(url_grupo + '/' + id_orden, data=json.dumps(data), timeout=15)
    print(resultado_envio.status_code)
    print(resultado_envio.content)
    if resultado_envio.status_code == 201:
        return 1 # Si el proveedor crea la orden
    else:
        return 0 # Si el proveedor no crea la orden



#Funcion a ejecutar en main, para restockear sku's
def restock():
    escribir('Llamada a restock')
    lista_stock_disponible = consultar_almacen_general() # {'sku': cantidad}
    escribir(f'stock disponible: {lista_stock_disponible}')
    # para cada ingrediente nuestro
    for i in ingredientes_nuestros:
        # si no tiene un mínimo de 5*lote de cantidad en almacen general, se manda a fabricar
        if str(i) not in lista_stock_disponible or lista_stock_disponible[str(i)] < 5*ingredientes_nuestros[i]['lote']:
            # obj es el objeto encontrado con ese parametro, created es un bool de si lo encontró o lo tuvo que crear
            obj, created = Contador.objects.get_or_create(sku=i)  # Usé este metodo que encontré porque lo encontré práctico, si falla reemplazar por un "if exists + filter"
            if obj.tick == 0:
                escribir(f'Se mandó a fabricar: {i}')
                fabricar_ingredientes(i, ingredientes_nuestros[i]['lote'] * 10)
            obj.tick += 1
            if obj.tick >= ingredientes_nuestros[i]['tiempo_produccion']/3:
                obj.tick = 0
            obj.save()
    # escribir('Restock terminó de ejecutar')
    # print(consultar_almacen_general())

# EMBAJADAS
# Función para decargar ordenes de compra de casilla FTP
def get_OC_embajadas_en_XML():
    # escribir('llamada a get_OC_embajadas_en_XML')
    host = URL_FTP                  #hard-coded
    port = PUERTO_FTP
    password = password_FTP               #hard-coded
    username = user_FTP    
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username = username, password = password)

        sftp = paramiko.SFTPClient.from_transport(transport)
        # escribir("Conexion casilla realizada")

        #OBTENER ORDENES DE COMPRA DE LAS EMBAJADAS EN XML
        files = sftp.listdir('/pedidos')
        #print(f"Files: {files}")
        for elem in files: 
            if elem == ".cache":
                continue
            #print(f"archivo xml: {elem}")
            #print(f"Los que hay de antes: {os.listdir(os.path.join(BASE_DIR, 'OC/OC_embajadas/'))}")
            #if f"{elem}" in set(os.listdir(os.path.join(BASE_DIR, 'OC/OC_embajadas/'))):
            #    os.remove(os.path.join(BASE_DIR, f"OC/OC_embajadas/{elem}"))
            sftp.get(f"/pedidos/{elem}", os.path.join(BASE_DIR, f"OC/OC_embajadas/{elem}"))

            # como ya lo descargué (lo tenemos en OC/embajadas/___.xml) 
            # => lo elimino de la casilla FTP
            sftp.remove(f"/pedidos/{elem}") 

        #CERRAR CONEXIÓN
        sftp.close()
        transport.close()
        # escribir("Conexion casilla cerrada")

    except Exception as e:
        escribir("Exception casillas ftp")
        print(e)

def crear_OC_embajadas_en_BD():
    try:
        oc_embajadas_xml = os.listdir(os.path.join(BASE_DIR, 'OC/OC_embajadas/'))
        # Abrimos y parseamos el fichero XML
        # escribir(f'{oc_embajadas_xml}')
        for orden in oc_embajadas_xml:
            if orden == 'auxiliar.txt':
                continue
            tree = ET.parse(os.path.join(BASE_DIR,f'OC/OC_embajadas/{orden}'))
            root = tree.getroot()
            for child in root:
                #print(f"tag: {child.tag} | value: {child.text}")
                tag = child.tag
                value = child.text
                # escribir(f'tag {tag} value {value}')
                
                if tag == "id":
                    # Obtener otros datos de la OC en el sistema bodega con el id 
                    consulta_inicial = 'GET'
                    
                    header_get_almacenes = {
                        'Content-Type': 'application/json',
                    }
                    res_orden = requests.get(f'{url_OC}/obtener/{value}', headers=header_get_almacenes)
                    escribir(f'linea 430: {json.loads(res_orden.text)}')
                    if len(json.loads(res_orden.text)) < 1:
                        continue
                    res_orden = json.loads(res_orden.text)[0]
                    #print(f"Resultado_orden: {res_orden}")
                    escribir(f'{res_orden}')
                
                    #crear OC en la base de datos:
                    if not(OrdenDeCompra.objects.filter(_id = res_orden["_id"]).exists()):
                        # Aceptar la orden en la API
                        mensaje = {
                            "_id": res_orden["_id"]
                        }
                        requests.post(url_OC + '/recepcionar/'+ res_orden["_id"], data= mensaje)
                        # Crear la orden en la base de datos
                        nueva_orden = OrdenDeCompra.objects.create(_id= res_orden['_id'], 
                            cliente = res_orden['cliente'],
                            proveedor = res_orden['proveedor'], 
                            sku = res_orden['sku'],
                            fechaEntrega = res_orden['fechaEntrega'],
                            cantidad = res_orden['cantidad'],
                            cantidadDespachada = res_orden['cantidadDespachada'],
                            precioUnitario = res_orden['precioUnitario'],
                            canal = res_orden['canal'],
                            estado = 'aceptada',
                            notas = '',
                            rechazo = '',
                            anulacion = '',
                            urlNotificacion = res_orden['urlNotificacion'],
                            created_at = res_orden['created_at'],
                            updated_at = res_orden['updated_at'])   
                        nueva_orden.save()
                        escribir('Orden embajada guardada en bdd')
                        # Como ya está en la base de datos no es necesario que se encuentre
                        # la ordenes de compra de las embajada en la carpeta OC/OC_embajadas
                        if f"{orden}" in set(os.listdir(os.path.join(BASE_DIR, 'OC/OC_embajadas/'))):
                            os.remove(os.path.join(BASE_DIR, f"OC/OC_embajadas/{orden}"))
                            #print(f"borrado: OC/OC_embajadas/{orden}")
        # escribir('crear OC terminó')
    except:
        escribir('Except crear OC embajadas')


def get_OC_embajadas_y_guardar_en_bd():
    escribir('EMPEZANDO GET OC EMBAJADAS')
    get_OC_embajadas_en_XML()
    crear_OC_embajadas_en_BD()
    escribir('TERMINANDO GET OC EMBAJADAS')


def escribir(texto):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open("probanding.txt", "a") as archivo:
        archivo.write(f'Tiempo: {current_time} Texto: {texto}\n')