from OC.funciones_OC import revisar_stock_OC, fabricar_ingredientes, restock, escribir, get_OC_embajadas_y_guardar_en_bd
from OC.funciones_vacunas import moveStock_recepcion_to_general, restock_grupos, chequear_ordenes_vacuna

def main():
    #probar cron
    escribir('Se corrió main')

    # manejo de bodegas
    moveStock_recepcion_to_general()

    # # manejo de embajadas
    # get_OC_embajadas_y_guardar_en_bd() #obtener OC de embajadas de casilla FTP y guarda en BD
    # chequear_ordenes_vacuna()  #revisar OC embajadas
    
    revisar_stock_OC() #revisar OC de otros grupos # manejo de ordenes de grupos

    # restock() #restock ingredientes propios
    # restock_grupos()  #restock pedir ingredientes a otros grupos

