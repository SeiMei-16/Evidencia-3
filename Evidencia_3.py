from collections import namedtuple
import sqlite3
from sqlite3 import Error
import sys
import datetime

Ticket = namedtuple("Ticket", ("descripcion", "cantidad", "precio"))

ventas = {}
folioComp = 0
try:
    with sqlite3.connect("Ventas_Ev3.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""SELECT VENTA.Folio, VENTA.Fecha, DETALLE.Descripcion, DETALLE.Cantidad, DETALLE.PrecioU \
                          FROM VENTA \
                          INNER JOIN DETALLE ON DETALLE.Folio = VENTA.Folio""")
        registros = cursor.fetchall()
        for folio, fecha, descripcion, cantidad, precio in registros:
            if folio != folioComp:
                tupla1 = ()
                tupla2 = ()
            comp = folio in tupla1
            fecha2 = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
            if comp == False:
                tupla1 = tupla1 + (folio, fecha2)
            detalle = Ticket(descripcion, cantidad, precio)
            tupla2 = tupla2 + (detalle,)
            ventas[tupla1] = tupla2
            folioComp = folio
            
except Error as e:
    print (e)
    print("No se encontraron las tablas, se procedera a crearlas")
    try:
        cursor.execute("CREATE TABLE IF NOT EXISTS VENTA (Folio INTEGER PRIMARY KEY, Fecha TEXT NOT NULL);")
        cursor.execute("""CREATE TABLE IF NOT EXISTS DETALLE (Descripcion TEXT NOT NULL, Cantidad INTEGER NOT NULL, PrecioU REAL NOT NULL, \
                          Folio INTEGER NOT NULL, FOREIGN KEY(Folio) REFERENCES VENTA(Folio));""")
        print("Tablas creadas exitosamente")
    except Error as e:
        print (e)
    except Exception:
        print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
            
except Exception:
    print(f'Ocurrio un problema {sys.exc_info()[0]}')
    ventas = {}
else:
    print("Se importo la base de datos con con exito")   
finally:
    if conn:
        conn.close()

continuar = True

while continuar:
    respuesta = 1
    menu = int(input('''
===============================================
                    MENU
===============================================
 
1.- Registrar venta
2.- Consultar ventas
3.- Consultar por fechas
4.- Salir

Seleccione la opcion que desea: '''))
    
    if menu == 1:
        while True:
            while respuesta == 1:
                respuesta2 = 1
                tupla_folio = ()
                tupla_tuplaNominada = ()
                comprobacion = ventas.keys()
                continuar2 = True
                folio = int(input("\nIngrese el folio de venta: "))
                for i in comprobacion:
                    comprobacion2 = str(folio) in str(i[0])
                    if comprobacion2 == True:
                        print("El folio ya esta en uso")
                        continuar2 = False
                        break
                if continuar2 == False: break
                fecha_capturada = input("Ingrese la fecha de la venta (dd/mm/aaaa): ")
                fecha_venta = datetime.datetime.strptime(fecha_capturada, "%d/%m/%Y").date()
                folio = str(folio)
                tupla_folio = tupla_folio + (folio,fecha_venta)
                while respuesta2 == 1:
                    descripcion_venta = str(input("Ingrese el articulo: "))
                    cantidad_venta = int(input("Ingrese la cantidad de articulos: "))
                    precio1 = int(input("Ingrese el precio individual: "))
                    precio2 = precio1 * cantidad_venta
                    IVA = precio2 * 0.16
                    precio_venta = precio2 + IVA
                    venta = Ticket(descripcion_venta, cantidad_venta, precio1)
                    tupla_tuplaNominada = tupla_tuplaNominada + (venta,)
                    print(f"El subtotal es de: {precio2}")
                    print(f"El IVA aplicable es de: {IVA}")
                    print(f"El precio total es de: {precio_venta}")
                    respuesta2 = int(input("¿Quiere seguir registrando articulos? [0 = NO, 1 = SI]: "))
                    if respuesta2 == 0 :
                        ventas[tupla_folio] = tupla_tuplaNominada
                        print("Se ha registrado la venta exitosamente")
                respuesta = int(input("¿Quiere seguir registrando ventas? [0 = NO, 1 = SI]: "))
                if respuesta == 0: break
            break
        
    elif menu == 2:
        print("\nListado completo de ventas:")
        print("Folio\tFecha\t\tDescripcion\t\t\tCantidad\tPrecio U\tSubtotal\tIVA\tTotal")
        print("-"*120)
        for folio, detalle  in ventas.items():
            contador = 0
            numVentas = len(ventas[folio])
            while contador < numVentas:
                subtotal = ventas[folio][contador].cantidad * ventas[folio][contador].precio
                iva = subtotal * 0.16
                total = subtotal + iva
                print(f"{folio[0]}\t{folio[1]}\t{ventas[folio][contador].descripcion}\t\t{ventas[folio][contador].cantidad}\t\t${ventas[folio][contador].precio}\t\t${subtotal}\t\t${iva}\t${total}")
                contador += 1
    
    elif menu == 3:
        fecha_consulta = str(input("\nIngrese la fecha de las ventas que desea consultar (dd/mm/aaaa): "))
        fecha_consulta_procesada = datetime.datetime.strptime(fecha_consulta, "%d/%m/%Y").date()
        print(f"\nListado de ventas en la fecha {fecha_consulta_procesada}:")
        print("Folio\tFecha\t\tDescripcion\t\t\tCantidad\tPrecio U\tSubtotal\tIVA\tTotal")
        print("-"*120)
        for folio, detalle  in ventas.items():
            contador = 0
            numVentas = len(ventas[folio])
            if folio[1] == fecha_consulta_procesada:
                while contador < numVentas:
                    subtotal = ventas[folio][contador].cantidad * ventas[folio][contador].precio
                    iva = subtotal * 0.16
                    total = subtotal + iva
                    print(f"{folio[0]}\t{folio[1]}\t{ventas[folio][contador].descripcion}\t\t{ventas[folio][contador].cantidad}\t\t${ventas[folio][contador].precio}\t\t${subtotal}\t\t${iva}\t${total}")
                    contador += 1
            
    elif menu == 4:
        try:
            with sqlite3.connect("Ventas_Ev3.db") as conn:
                cursor = conn.cursor()
                for folio, detalle  in ventas.items():
                    contador = 0
                    numVentas = len(ventas[folio])
                    DicVENTA = {"Folio":folio[0], "Fecha":folio[1]}
                    cursor.execute("INSERT INTO VENTA VALUES(:Folio, :Fecha)", DicVENTA)
                    while contador < numVentas:
                        DicDETALLE = {"Descripcion":detalle[contador].descripcion, "Cantidad":detalle[contador].cantidad,
                                      "PrecioU":detalle[contador].precio, "Folio":folio[0]}
                        cursor.execute("INSERT INTO DETALLE VALUES(:Descripcion, :Cantidad, :PrecioU, :Folio)", DicDETALLE)
                        contador += 1
        except Error as e:
            print (e)
        except Exception:
            print(f"Se produjo el siguiente error: {sys.exc_info()[0]}")
        else:
            print(f"La exportacion a la base de datos ha sido exitosa")
            print("¡Gracias por usar nuestro sistema!")
            continuar = False
        finally:
            if conn:
                conn.close()

        
    else:
        print("Opcion no valida")
        