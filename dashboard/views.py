# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import Dashboard
from django.shortcuts import render, get_object_or_404
from django.urls import reverse


from rest_framework.response import Response
import requests
from base64 import b64encode, urlsafe_b64encode
from hashlib import sha1
import hmac
import json

from OC.models import OrdenDeCompra
from dashboard.models import Dashboard


#DESARROLLO:
# TOKEN = "5j8onuImEaP9TQ:"
# URL_API = "https://dev.api-bodega.2021-1.tallerdeintegracion.cl/bodega"


#PRODUCCIÓN:
TOKEN = "x$BLTe5$Dl;iDMO"
URL_API = "https://api-bodega.2021-1.tallerdeintegracion.cl/bodega"

#SKU_VACUNA = 10001
SKU_VACUNAS = [10001, 10002, 10003, 10004, 10005, 10006]
ID_ORDEN_DE_COMPRA_G17 = "60bd2a763f1b6100049f1457"

SKUS_ROWS = { #solo los compuestos que producimos nosotros (grupo 17)
  100: 0,
  109: 1,
  110: 2,
  112: 3,
  117: 4,
  118: 5,
  119: 6,
  121: 7,
  125: 8,
  128: 9,
  129: 10
}

#GRUPOS_COLS: GRUPO k -> j = k - 1 

# OC_ID_GRUPOS = { #DE DESARROLLO
#   "60bd2a763f1b6100049f1447": 1,
#   "60bd2a763f1b6100049f1448": 2,
#   "60bd2a763f1b6100049f1449": 3, 
#   "60bd2a763f1b6100049f144a": 4,
#   "60bd2a763f1b6100049f144b": 5,
#   "60bd2a763f1b6100049f144c": 6,
#   "60bd2a763f1b6100049f144d": 7,
#   "60bd2a763f1b6100049f144e": 8,
#   "60bd2a763f1b6100049f144f": 9,
#   "60bd2a763f1b6100049f1450": 10,
#   "60bd2a763f1b6100049f1451": 11,
#   "60bd2a763f1b6100049f1452": 12,
#   "60bd2a763f1b6100049f1453": 13, 
#   "60bd2a763f1b6100049f1454": 14,
#   "60bd2a763f1b6100049f1455": 15,
#   "60bd2a763f1b6100049f1456": 16,
#   "60bd2a763f1b6100049f1457": 17,
#   "60bd2a763f1b6100049f1458": 18,
#   "60bd2a763f1b6100049f1459": 19,
#   "60bd2a763f1b6100049f145a": 20, 
#   "60bd2a763f1b6100049f145b": 21,
#   "60bd2a763f1b6100049f145c": 22, 
#   "60bd2a763f1b6100049f145d": 23,
#   "60bd2a763f1b6100049f145e": 24,
#   "60bd2a763f1b6100049f145f": 25,
# }
OC_ID_GRUPOS = { #DE PRODUCCION
 "60caa3af31df040004e88de4": 1,
 "60caa3af31df040004e88de5": 2,
 "60caa3af31df040004e88de6": 3,
 "60caa3af31df040004e88de7": 4,
 "60caa3af31df040004e88de8": 5,
 "60caa3af31df040004e88de9": 6,
 "60caa3af31df040004e88dea": 7,
 "60caa3af31df040004e88deb": 8,
 "60caa3af31df040004e88dec": 9,
 "60caa3af31df040004e88ded": 10,
 "60caa3af31df040004e88dee": 11,
 "60caa3af31df040004e88def": 12,
 "60caa3af31df040004e88df0": 13,
 "60caa3af31df040004e88df1": 14,
 "60caa3af31df040004e88df2": 15,
 "60caa3af31df040004e88df3": 16,
 "60caa3af31df040004e88df4": 17,
 "60caa3af31df040004e88df5": 18,
 "60caa3af31df040004e88df6": 19,
 "60caa3af31df040004e88df7": 20,
 "60caa3af31df040004e88df8": 21,
 "60caa3af31df040004e88df9": 22,
 "60caa3af31df040004e88dfa": 23,
 "60caa3af31df040004e88dfb": 24, 
 "60caa3af31df040004e88dfc": 25,
}

COMPUESTOS = {
  #Excipientes
  "100":	"1,2-diestearol-sn-glicero-3-fosfocolina",
  "102":	"Acetato de sodio trihidrato",
  "103":	"Ácido acético",
  "104":	"Ácido cítrico monohidrato",
  "107":	"ALC-0159",
  "108":	"ALC-0315",
  "109":	"Citrato trisódico dihidrato",
  "110":	"Clorhidrato de trometamol",
  "111":	"Cloruro de magnesio hexahidrato",
  "112":	"Cloruro de potasio",
  "113":	"Cloruro de sodio",
  "114":	"Colesterol",
  "115":	"Dihidrogenofosfato de sodio",
  "116":	"EDTA disódico dihidrato",
  "117":	"Etanol",
  "118":	"Fosfato monobásico de potasio",
  "119":	"Fosfato sódico dibásico dihidrato",
  "120":	"Hidrogenofosfato de disodio",
  "121":	"Hidróxido de aluminio",
  "122":	"Hidróxido de sodio",
  "124":	"L-Histidine",
  "125":	"L-Histidine hydrochloride monohydrate",
  "126":	"Lípido SM-102",
  "127":	"Polietilenglicol",
  "128":	"Polisorbato 80",
  "129":	"Sacarosa",
  "132":	"Trometamol",
  #otros mas raros pero tbm son compuestos para vacunas
  "1000":	"mRNA",
  "1001":	"Antígeno SARS-CoV-2 inactivado",
  "1002":	"Partículas virales de ChAdOx1-S",
  "1003":	"Adenovirus tipo 26 (Ad26)"
}

def index(request): #GET /dashboard/
    # print(f"Request1: {request}")
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #context = {'latest_question_list': latest_question_list}
    #return render(request, 'polls/index.html', context)

    def get_data():

        """ OBTENER LA OCUPACION DE BODEGA (obtener la ocupacion de los almacenes)"""
        if request.method == 'GET':
            #print(f"Compuestos.keys: {COMPUESTOS.keys()} el set: {set(COMPUESTOS.keys())}")
            consulta_inicial = 'GET'
            token = TOKEN
            hash_hmac = hmac.new(token.encode(), consulta_inicial.encode(), sha1).digest()
            request_hash = b64encode(hash_hmac).decode('utf-8')

            header_get_almacenes = {
              'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash), 
              'Content-Type': 'application/json',
              'Key': token
            }
            res_almacenes = requests.get(f"{URL_API}/almacenes", 
                            headers=header_get_almacenes)
            lista_almacenes = json.loads(res_almacenes.text)

            #print(f"Lista de almacenes: {lista_almacenes}")
            #pendiente mañana mostrar ocupacion de bodegas con esta informacion.
            
            """OBTENER LAS VACUNAS EN BODEGA"""
            vacunas_no_vencidas_bodega = []
            #OBTENER LAS VACUNAS EN BODEGA NO VENCIDAS.

            for SKU_VACUNA in SKU_VACUNAS:
              for almacen in lista_almacenes:
                  consulta_almacen = f"GET{almacen['_id']}{SKU_VACUNA}"
                  hash_hmac_almacen = hmac.new(token.encode(), consulta_almacen.encode(), sha1).digest()
                  request_hash_almacen = b64encode(hash_hmac_almacen).decode('utf-8')
  
                  header_get_almacen = {
                  'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash_almacen), 
                  'Content-Type': 'application/json',
                  'Key': token
                  }
  
                  res_almacen = requests.get(f"{URL_API}/stock?almacenId={almacen['_id']}&sku={SKU_VACUNA}", headers=header_get_almacen)
  
                  vacunas_no_vencidas = json.loads(res_almacen.text)
                  #print(f"Vacunas no vencidas en almacen actual: {vacunas_no_vencidas}")
                  if vacunas_no_vencidas != []: 
                      for vacuna in vacunas_no_vencidas:
                          vacunas_no_vencidas_bodega.append(vacunas_no_vencidas)

            #print(f"Vacunas no vencidas en bodega: {vacunas_no_vencidas_bodega}")


            """ OBTENER LOS COMPUESTOS QUE ESTÁN EN BODEGA"""
            compuestos_no_vencidos_bodega = []
            #OBTENER LAS VACUNAS EN BODEGA NO VENCIDAS.
            for almacen in lista_almacenes:
                consulta_almacen = f"GET{almacen['_id']}"
                hash_hmac_almacen = hmac.new(token.encode(), consulta_almacen.encode(), sha1).digest()
                request_hash_almacen = b64encode(hash_hmac_almacen).decode('utf-8')

                header_get_almacen = {
                'Authorization': 'INTEGRACION grupo17:{}'.format(request_hash_almacen), 
                'Content-Type': 'application/json',
                'Key': token
                }

                res_almacen = requests.get(f"{URL_API}/skusWithStock?almacenId={almacen['_id']}", headers=header_get_almacen)

                skus_no_vencidos = json.loads(res_almacen.text)
                #print(f"SKUS no vencidos en almacen actual: {skus_no_vencidos}")
                """
                eso retorna:
                [{
                    "_id":"118",
                    "total":6
                }]
                """
                for elem in skus_no_vencidos:
                    #si el sku actual es un compuesto -> lo agrego a la lista
                    # de compuestos no vencidos en bodega
                    compuestos = set(COMPUESTOS.keys())
                    if elem["_id"] in compuestos:
                        compuestos_no_vencidos_bodega.append(elem)
            #print(f"Compuestos no vencidos bodega: {compuestos_no_vencidos_bodega}")


            """INFORMACIÓN DASHBOARD PARTE 2"""

            """Obtener ordenes de compra enviados hacia nuestra bodega (otros grupos) 
            o enviados desde nuestra bodega (nosotros enviamos)"""
            ordenes_de_compra = OrdenDeCompra.objects.all()
            #print(f"Ordenes de compra todos: {ordenes_de_compra}")
            #ordenes_de_compra_enviados = OrdenDeCompra.objects.filter(cliente = "60bd2a763f1b6100049f1457")
            #print(f"Ordenes de compra enviados: {ordenes_de_compra_enviados}")
          
            return (lista_almacenes, vacunas_no_vencidas_bodega, compuestos_no_vencidos_bodega, ordenes_de_compra)



    def handle_data_grafico_barras(lista_almacenes):
        #print(f"Lista almacenes: {lista_almacenes}")
        almacenes_porcentaje_ocupacion = []
        for i, almacen in enumerate(lista_almacenes):
            espacio_ocupado = almacen["usedSpace"]
            espacio_total = almacen["totalSpace"]

            pulmon, despacho, recepcion = almacen["pulmon"], almacen["despacho"], almacen["recepcion"]
            tipo = 'Sin tipo especificado'
            if pulmon:
              tipo = 'Pulmón'
            elif despacho:
              tipo = 'de Despacho'
            elif recepcion:
              tipo = 'de Recepción'

            porcentaje_ocupado = (espacio_ocupado / espacio_total) * 100
            almacen_data = {"name": f"Almacen {tipo} \n (ocupado {espacio_ocupado} de {espacio_total}) \n", "y": porcentaje_ocupado}
            almacenes_porcentaje_ocupacion.append(almacen_data)

        #print(f"almacenes porcentaje ocupacion:{almacenes_porcentaje_ocupacion}")
        
        grafico_barras_h_data = {
            "chart": {
              "type": 'column'
            },
            "title": {
              "text": 'Porcentaje de ocupación en la bodega'
            },
            "subtitle": {
              "text": 'Separado por almacén'
            },
            "accessibility": {
              "announceNewData": {
                "enabled": "true"
              }
            },
            "xAxis": {
              "type": 'category',
              "title": {
                "text": 'Almacen i (ocupado X de total Y)'
              }
            },
            "yAxis": {
              "title": {
                "text": 'Porcentaje del almacen ocupado'
              }
            
            },
            "plotOptions": {
              "series": {
                "borderWidth": 0,
                "dataLabels": {
                  "enabled": "true",
                  "format": '{point.y:.1f}%',
                },
               },
            },
            
            "series": [
              {
                "name": "Porcentaje de ocupación",
                "colorByPoint": "true",
                "data": almacenes_porcentaje_ocupacion
              }
            ],
        }
            

        return grafico_barras_h_data


    def handle_data_grafico_torta(compuestos_no_vencidos_bodega):


        """
        compuestos_no_vencidos_bodega = [{ "_id":"118", "total":6}, {"_id": "107, "total": 10}] #un ejemplo posible
        """
        """
        Estructura deseada:
        data_grafico_torta = [
                    { "name": 'Compuesto SKU1', "y": 10 },
                    { "name": 'CompuestoS SKU2', "y": 10 },
                    { "name": 'Compuesto SKU3', "y": 10 },
                    { "name": 'Compuesto SKU4', "y": 10 },
                    { "name": 'Compuesto SKU5', "y": 5 }
                  ]
        """



        data_grafico_torta = []
        
        for compuesto in compuestos_no_vencidos_bodega:
            #print(f"Forma del objeto compuesto: {compuesto}")
            item = {"name": f"{COMPUESTOS[compuesto['_id']]} \n (SKU: {compuesto['_id']}) ", "y": compuesto["total"]}
            data_grafico_torta.append(item)

        #data_grafico_torta.append(  {"name": "Compuesto 100", "y": 3})

        if data_grafico_torta == []:
            data_grafico_torta = [ {"name": "No hay compuestos en bodega", "y": 0}]

        grafico_de_torta_data = {
                "chart": {
                  "plotShadow": "false",
                  "type": 'pie'
                },
                "title": {
                  "text": 'Cantidad de los compuestos en Bodega'
                },
                "tooltip": {
                  "pointFormat": '{series.name}: <b>{point.percentage:.1f}%</b>'
                },
                "plotOptions": {
                  "pie": {
                    "allowPointSelect": "true",
                    "cursor": 'pointer',
                    "dataLabels": {
                      "enabled": "true",
                      "format": '<b>{point.name}</b>: {point.y}',
                      "connectorColor": 'silver'
                    }
                  }
                },
                "series": [{
                  "name": 'Porcentaje',
                  "data": data_grafico_torta,
                }]
              }
        
        return grafico_de_torta_data


    def handle_data_grafico_heat_map(ordenes_de_compra):
      #i: grupo i
      #j: SKU <num> j
      #valor
      #[j, i, valor]

      # j = <grupo num> - 1
      # i = 100, 107, 108, .... <-> 0, 1, 2, ..
      grafico_heat_map_data2 = []

      posiciones_ocupadas = set()
      for orden in ordenes_de_compra:
              cliente = orden.cliente
              proveedor = orden.proveedor
              #_id = orden._id
              sku = orden.sku
              #fechaEntrega = orden.fechaEntrega
              cantidad = orden.cantidad
              #cantidadDespachada = orden.cantidadDespachada
              #precioUnitario = orden.precioUnitario
              #canal = orden.canal
              estado = orden.estado
              #notas = orden.notas
              #rechazo = orden.rechazo
              #anulacion = orden.anulacion
              #urlNotificacion = orden.urlNotificacion
              
              #Chequear que sea un producto.
              compuestos2 = [ int(elem) for elem in COMPUESTOS.keys()]
              #print(f"Compuestos 2: {compuestos2}")
              if sku not in compuestos2:
                continue
              #si llega acá es porque la orden de compra está asociada a un producto.

              if SKUS_ROWS.get(sku) is None:
                SKUS_ROWS[sku] = None
              
              pos_i = SKUS_ROWS[sku] if SKUS_ROWS[sku] is not None else None# 0 .. 25 (son 25 grupos, del 1 al 26)

              if OC_ID_GRUPOS.get(cliente) is None:
                OC_ID_GRUPOS[cliente] = None
              
              pos_j = OC_ID_GRUPOS[cliente] - 1 if OC_ID_GRUPOS[cliente] is not None else None # 0, ... 5 (son 5 SKUS que son productos)
              

              #print(f"Cliente: {cliente} (Grupo: {OC_ID_GRUPOS[cliente]}) | proveedor: {proveedor}  (Grupo: {OC_ID_GRUPOS[proveedor]})| sku: {sku} {type(sku)}| cantidad: {cantidad}")
              #print(f"(j, i, value) <-> {pos_j, pos_i, cantidad}")
              #print(f"Estado: {estado}")


              #pos_j = 0 # 0 .. 25 (son 25 grupos, del 1 al 26)
              #pos_i = 10 # 0, ... 5 (son 5 SKUS que son productos)
              if pos_i is not None and pos_j is not None and estado == "completada":
                item = [pos_j, pos_i, cantidad]
                grafico_heat_map_data2.append(item)
                posiciones_ocupadas.add((pos_i, pos_j))

      for j in range(0, 26):
        for i in range(0, 11): #son 10 productos por el momento.
          if (i, j) not in posiciones_ocupadas:
            item = [j, i, 0]
            if j == 16:
              item[-1] = ''
            grafico_heat_map_data2.append(item)



      #print(f"Grafico heat mapa data 2: {grafico_heat_map_data2}")
      return grafico_heat_map_data2



    def handle_data_tarjeta_resultados_2(ordenes_de_compra):
      #retornar la cantidad de vacunas fabricadas
      if len(Dashboard.objects.all()) > 0:
        dashboard = Dashboard.objects.all()[0]
        return dashboard.vacunas_fabricadas
      else:
        return 0
      

    lista_almacenes, vacunas_no_vencidas_bodega, compuestos_no_vencidos_bodega, ordenes_de_compra = get_data()
    #print(f"{'='*50}")
    # print(f"Lista de almacenes: {lista_almacenes}")
    # print(f"Vacunas no vencidas en bodega: {vacunas_no_vencidas_bodega}")
    # print(f"Compuestos no vencidos en bodega: {compuestos_no_vencidos_bodega}")


    grafico_barras_h_data = handle_data_grafico_barras(lista_almacenes)
    grafico_de_torta_data = handle_data_grafico_torta(compuestos_no_vencidos_bodega)
    tarjeta_resultados_data = len(vacunas_no_vencidas_bodega) #pendiente bien

    grafico_heat_map_data = handle_data_grafico_heat_map(ordenes_de_compra)
    tarjeta_resultados2_data = handle_data_tarjeta_resultados_2(ordenes_de_compra)


    context = {
        'grafico_barras_h': grafico_barras_h_data,
        'grafico_de_torta': grafico_de_torta_data,
        'tarjeta_resultados': tarjeta_resultados_data,
        
        'grafico_heat_map': grafico_heat_map_data,
        'tarjeta_resultados2': tarjeta_resultados2_data,

    }
    return render(request, 'dashboard/index.html', context)

# Leave the rest of the views (detail, results, vote) unchanged
