from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

#PRODUCCION
URL_OC_P = 'https://oc.2021-1.tallerdeintegracion.cl/oc'
URL_BODEGA_P = 'https://api-bodega.2021-1.tallerdeintegracion.cl/bodega'
SELF_ID_P = '60caa3af31df040004e88df4'
TOKEN_P = "x$BLTe5$Dl;iDMO"
USER_FTP_P = 'grupo17_produccion'
PASS_FTP_P = 'v6Sjd5n3FWM21hdlSRxN'


#DESARROLLO
URL_OC_D = 'https://dev.oc.2021-1.tallerdeintegracion.cl/oc'
URL_BODEGA_D = 'https://dev.api-bodega.2021-1.tallerdeintegracion.cl/bodega'
SELF_ID_D= '60bd2a763f1b6100049f1457' 
TOKEN_D = "5j8onuImEaP9TQ:"
USER_FTP_D = 'grupo17_desarrollo'
PASS_FTP_D = 'dJdoxjah3l5fA2RCSKla'

URL_FTP = 'beirut.ing.puc.cl'
PUERTO_FTP = 22
PROTOCOLO_FTP = 'sftp'

ingredientes_nuestros = {
  100: {'lote': 5, 'tiempo_produccion': 40, 'duracion':36},
  109: {'lote': 2, 'tiempo_produccion': 20, 'duracion':14},
  110: {'lote': 6, 'tiempo_produccion': 25, 'duracion':13},
  112: {'lote': 5, 'tiempo_produccion': 10, 'duracion':4},
  117: {'lote': 20, 'tiempo_produccion': 20, 'duracion':16},
  118: {'lote': 4, 'tiempo_produccion': 30, 'duracion':12},
  119: {'lote': 14, 'tiempo_produccion': 45, 'duracion':6},
  121: {'lote': 3, 'tiempo_produccion': 30, 'duracion':5},
  125: {'lote': 4, 'tiempo_produccion': 40, 'duracion':10},
  128: {'lote': 3, 'tiempo_produccion': 45, 'duracion':18},
  129: {'lote': 10, 'tiempo_produccion': 15, 'duracion':36},
  1000: {'lote': 8, 'tiempo_produccion': 50, 'duracion':1},
  1001: {'lote': 5, 'tiempo_produccion': 40, 'duracion':1},
  1002: {'lote': 3, 'tiempo_produccion': 20, 'duracion':2},
  1003: {'lote': 5, 'tiempo_produccion': 30, 'duracion':1}
}

ingredientes_grupos = {
  102: {'lote': 8, 'tiempo_produccion': 30, 'grupos': [1,4,5,8,11,16,12,3,6], 'duracion':6},
  103: {'lote': 9, 'tiempo_produccion': 45, 'grupos': [1,4,7,10,16,20,21,5,8], 'duracion':30},
  104: {'lote': 6, 'tiempo_produccion': 20, 'grupos': [1,4,7,10,13,16,19,22,25,2], 'duracion':4},
  107: {'lote': 7, 'tiempo_produccion': 40, 'grupos': [1,3,10,11,20,21,4,7], 'duracion':16},
  108: {'lote': 18, 'tiempo_produccion': 25, 'grupos': [3,6,8,13,18,23,9,10], 'duracion':8},
  111: {'lote': 18, 'tiempo_produccion': 25, 'grupos': [12,15,18,21,24,3,7,11,19,23], 'duracion':8},
  113: {'lote': 12, 'tiempo_produccion': 45, 'grupos': [1,3,7,10,11,18,15,16,21,22,20,23,25,2,8], 'duracion':32},
  114: {'lote': 14, 'tiempo_produccion': 20, 'grupos': [4,5,15,21,22,23,25,24,1], 'duracion':8},
  115: {'lote': 20, 'tiempo_produccion': 50, 'grupos': [5,7,10,11,12,19,20,21,23,25], 'duracion':18},
  116: {'lote': 10, 'tiempo_produccion': 20, 'grupos': [15,2,6,10,14,18,22,1,5,9], 'duracion':22},
  120: {'lote': 5, 'tiempo_produccion': 20, 'grupos': [1,2,4,16,18,23,24,25,8,9], 'duracion':4},
  122: {'lote': 10, 'tiempo_produccion': 80, 'grupos': [4,9,14,19,24,6,11,16,21,1], 'duracion':18},
  124: {'lote': 5, 'tiempo_produccion': 20, 'grupos': [3,4,5,6,7,9,10,11,12,13,14], 'duracion':8},
  126: {'lote': 10, 'tiempo_produccion': 45, 'grupos': [2,3,8,19,23,24,25,12,13], 'duracion':9},
  127: {'lote': 5, 'tiempo_produccion': 50, 'grupos': [5,9,15,18,20,21,23,14,16], 'duracion':27},
  132: {'lote': 14, 'tiempo_produccion': 15, 'grupos': [9,12,13,15,22,25,18,19], 'duracion': 24}
}


ids_grupos_desarrollo = {
    '60bd2a763f1b6100049f1447': '1',
    '60bd2a763f1b6100049f1448': '2',
    '60bd2a763f1b6100049f1449': '3',
    '60bd2a763f1b6100049f144a': '4',
    '60bd2a763f1b6100049f144b': '5',
    '60bd2a763f1b6100049f144c': '6',
    '60bd2a763f1b6100049f144d': '7',
    '60bd2a763f1b6100049f144e': '8',
    '60bd2a763f1b6100049f144f': '9',
    '60bd2a763f1b6100049f1450': '10',
    '60bd2a763f1b6100049f1451': '11',
    '60bd2a763f1b6100049f1452': '12',
    '60bd2a763f1b6100049f1453': '13',
    '60bd2a763f1b6100049f1454': '14',
    '60bd2a763f1b6100049f1455': '15',
    '60bd2a763f1b6100049f1456': '16',
    '60bd2a763f1b6100049f1457': '17', 
    '60bd2a763f1b6100049f1458': '18',
    '60bd2a763f1b6100049f1459': '19',
    '60bd2a763f1b6100049f145a': '20',
    '60bd2a763f1b6100049f145b': '21',
    '60bd2a763f1b6100049f145c': '22',
    '60bd2a763f1b6100049f145d': '23',
    '60bd2a763f1b6100049f145e': '24', 
    '60bd2a763f1b6100049f145f': '25'   
} 
ids_grupos_produccion = {
    '60caa3af31df040004e88de4': '1',
    '60caa3af31df040004e88de5': '2',
    '60caa3af31df040004e88de6': '3',
    '60caa3af31df040004e88de7': '4',
    '60caa3af31df040004e88de8': '5',
    '60caa3af31df040004e88de9': '6',
    '60caa3af31df040004e88dea': '7',
    '60caa3af31df040004e88deb': '8',
    '60caa3af31df040004e88dec': '9',
    '60caa3af31df040004e88ded': '10',
    '60caa3af31df040004e88dee': '11',
    '60caa3af31df040004e88def': '12',
    '60caa3af31df040004e88df0': '13',
    '60caa3af31df040004e88df1': '14',
    '60caa3af31df040004e88df2': '15',
    '60caa3af31df040004e88df3': '16',
    '60caa3af31df040004e88df4': '17',
    '60caa3af31df040004e88df5': '18',
    '60caa3af31df040004e88df6': '19',
    '60caa3af31df040004e88df7': '20',
    '60caa3af31df040004e88df8': '21',
    '60caa3af31df040004e88df9': '22',
    '60caa3af31df040004e88dfa': '23',
    '60caa3af31df040004e88dfb': '24',
    '60caa3af31df040004e88dfc': '25'
}

ids_almacen_recepcion_desarrollo = {
    '1': '60bd3477f955380004eda9f4',
    '2': '0bd3477f955380004eda9f8',
    '3': '60bd3477f955380004eda9fc',
    '4': '60bd3477f955380004edaa00',
    '5': '60bd3477f955380004edaa04',
    '6': '60bd3477f955380004edaa08',
    '7': '60bd3477f955380004edaa0c',
    '8': '60bd3477f955380004edaa10',
    '9': '60bd3477f955380004edaa14',
    '10': '60bd3477f955380004edaa18',
    '11': '60bd3477f955380004edaa1c',
    '12': '60bd3477f955380004edaa20',
    '13': '60bd3477f955380004edaa24',
    '14': '60bd3477f955380004edaa28',
    '15': '60bd3477f955380004edaa2c',
    '16': '60bd3477f955380004edaa30',
    '17': '60bd3477f955380004edaa34',
    '18': '60bd3477f955380004edaa38',
    '19': '60bd3477f955380004edaa3c',
    '20': '60bd3477f955380004edaa40',
    '21': '60bd3477f955380004edaa44',
    '22': '60bd3477f955380004edaa48',
    '23': '60bd3477f955380004edaa4c',
    '24': '60bd3477f955380004edaa50',
    '25': '60bd3477f955380004edaa54'
}

ids_almacen_recepcion_produccion = {
    '1': '60ccc5559092f7000423929a',
    '2': '60ccc5559092f7000423929e',
    '3': '60ccc5559092f700042392a2',
    '4': '60ccc5559092f700042392a6',
    '5': '60ccc5559092f700042392aa',
    '6': '60ccc5559092f700042392ae',
    '7': '60ccc5559092f700042392b2',
    '8': '60ccc5559092f700042392b6',
    '9': '60ccc5559092f700042392ba',
    '10': '60ccc5559092f700042392be',
    '11': '60ccc5559092f700042392c2',
    '12': '60ccc5559092f700042392c6',
    '13': '60ccc5559092f700042392ca',
    '14': '60ccc5559092f700042392ce',
    '15': '60ccc5559092f700042392d2',
    '16': '60ccc5559092f700042392d6',
    '17': '60ccc5559092f700042392da',
    '18': '60ccc5559092f700042392de',
    '19': '60ccc5559092f700042392e2',
    '20': '60ccc5559092f700042392e6',
    '21': '60ccc5559092f700042392ea',
    '22': '60ccc5559092f700042392ee',
    '23': '60ccc5559092f700042392f2',
    '24': '60ccc5559092f700042392f6',
    '25': '60ccc5559092f700042392fa'
}

url_recepcion_OC= {
    '1': 'http://aysen1.ing.puc.cl/ordenes-compra',
    '2': 'http://aysen2.ing.puc.cl/storage/ordenes-compra',
    '3': 'http://aysen3.ing.puc.cl/api/ordenes-compra',
    '4': 'http://aysen4.ing.puc.cl/ordenes-compra',
    '5': 'http://aysen5.ing.puc.cl/ordenes-compra',
    '6': 'http://aysen6.ing.puc.cl/ordenes-compra',
    '7': 'http://aysen7.ing.puc.cl/ordenes-compra',
    '8': 'http://aysen8.ing.puc.cl/ordenes-compra',
    '9': 'http://aysen9.ing.puc.cl/ordenes-compra',
    '10': 'http://aysen10.ing.puc.cl/ordenes-compra',
    '11': 'http://aysen11.ing.puc.cl/ordenes-compra',
    '12': 'http://aysen12.ing.puc.cl/ordenes-compra',
    '13': 'http://aysen13.ing.puc.cl/ordenes-compra',
    '14': 'http://aysen14.ing.puc.cl/ordenes-compra',
    '15': 'http://aysen15.ing.puc.cl/ordenes-compra',
    '16': 'http://aysen16.ing.puc.cl/recepcionar',
    '17': 'http://aysen17.ing.puc.cl/ordenes-compra/{_id}',
    '18': 'http://aysen18.ing.puc.cl/ordenes-compra',
    '19': 'http://aysen19.ing.puc.cl/ordenes-compra',
    '20': 'http://aysen20.ing.puc.cl/ordenes-compra',
    '21': 'http://aysen21.ing.puc.cl/ordenes-compra',
    '22': 'http://aysen22.ing.puc.cl/ordenes-compra',
    '23': 'http://aysen23.ing.puc.cl/ordenes-compra',
    '24': 'http://aysen24.ing.puc.cl/ordenes-compra',
    '25': 'http://aysen25.ing.puc.cl/ordenes-compra',
}


## datos de vacuna
INGREDIENTES_VACUNA = {
  '10001': {
    '1000': 12,
    '107': 6,
    '108': 6,
    '100': 6,
    '114': 6,
    '112': 6,
    '119': 6,
    '129': 12,
    '113': 6,
    '118': 6
  },

  '10002': {
    '1001': 8,
    '121': 8,
    '120': 16,
    '115': 8,
    '113': 16
  },

  '10005': {
    '1000': 12,
    '126': 4,
    '114': 4,
    '100': 4,
    '127': 4,
    '132': 8,
    '110': 4,
    '103': 4,
    '102': 4,
    '129': 4
  },

  '10003': {
    '1002': 5,
    '121': 5,
    '124': 10,
    '125': 5,
    '111': 5,
    '128': 5,
    '117': 5,
    '129': 5,
    '113': 5,
    '116': 10
  },

  '10004': {
    '1003': 10,
    '104': 10,
    '109': 5,
    '117': 5,
    '128': 5,
    '113': 5,
    '122': 10,
  },

  '10006': {
    '1003': 9,
    '113': 9,
    '129': 9,
    '111': 9,
    '116': 9,
    '128': 9,
    '117': 18,
  }
}

LOTES_POR_VACUNA = {
  '10001': 6,
  '10002': 8,
  '10005': 4,
  '10003': 5,
  '10004': 5,
  '10006': 9,
}

URL_OBTENER_STOCK_GRUPOS = {
  '1': 'http://aysen1.ing.puc.cl/stocks',
  '2': 'http://aysen2.ing.puc.cl/storage/stocks',
  '3': 'http://aysen3.ing.puc.cl/api/stocks',
  '4': 'http://aysen4.ing.puc.cl/stocks',
  '5': 'http://aysen5.ing.puc.cl/stocks',
  '6': 'http://aysen6.ing.puc.cl/stocks',
  '7': 'http://aysen7.ing.puc.cl/stocks',
  '8': 'http://aysen8.ing.puc.cl/stocks',
  '9': 'http://aysen9.ing.puc.cl/stocks',
  '10': 'http://aysen10.ing.puc.cl/stocks',
  '11': 'http://aysen11.ing.puc.cl/stocks',
  '12': 'http://aysen12.ing.puc.cl/stocks',
  '13': 'http://aysen13.ing.puc.cl/stocks',
  '14': 'http://aysen14.ing.puc.cl/stocks',
  '15': 'http://aysen15.ing.puc.cl/stocks',
  '16': 'http://aysen16.ing.puc.cl/stocks',
  '17': 'http://aysen17.ing.puc.cl/stocks',
  '18': 'http://aysen18.ing.puc.cl/stocks',
  '19': 'http://aysen19.ing.puc.cl/stocks',
  '20': 'http://aysen20.ing.puc.cl/stocks',
  '21': 'http://aysen21.ing.puc.cl/stocks',
  '22': 'http://aysen22.ing.puc.cl/stocks',
  '23': 'http://aysen23.ing.puc.cl/stocks',
  '24': 'http://aysen24.ing.puc.cl/stocks',
  '25': 'http://aysen25.ing.puc.cl/stocks',
}

SKU_VACUNAS = [10001, 10002, 10003, 10004, 10005, 10006]
