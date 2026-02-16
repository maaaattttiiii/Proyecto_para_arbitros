colegio = {}
def registro():
    dni = input("Ingrese el DNI del arbitro que quiere registrar: ")
    nombre = input("Ingrese el Nombre: ")
    apellido = input("Ingrese el Apellido: ")
    categoria = input("Ingrese la categoría: ")
    
    arbitro = { "nombre" : nombre,
               "apellido" : apellido,
               "categoria" : categoria,
               "partidos" : [],
               "pagos" : {},
               "evaluaciones" : []}
    
    colegio[dni] = arbitro
    print(f"{nombre}, {apellido}. Registrado con éxito")



def designar():
    dni = input("Ingrese el DNI de el arbitro que quiere designar: ")
    
    if dni in colegio:
        dia = input("Ingrese el dia que dirigio en numero: ")
        mes = input("Ingrese el mes que dirigio en numero: ")
        plata = input("Ingrese cuanto gano en pesos por el dia: ")

        trabajo = (dia, mes , plata )
        colegio[dni]["partidos"].append(trabajo)

    else:
        print("no existe el arbitro que busca")

def desempeño():
    dni = input("Ingrese el DNI de el arbitro que quiere designar: ")
    
    if dni in colegio:
        dia = input("Ingrese el dia que dirigio en numero: ")
        mes = input("Ingrese el mes que dirigio en numero: ")
        ubicacion = pedir_bool("¿Se ubico bien en la cancha la mayoria del partido?")
        señas = pedir_bool("¿Sus señalización fue buena?")
        control = pedir_bool("¿Buen control de juego?")
        compañerismo = pedir_bool("¿Dio charla pre partido y estuvo atento a sus compañeros?")

        partido = { "dia" : dia,
                   "mes" : mes,
                   "ubicacion" : ubicacion, 
                   "señas" : señas,
                   "control" : control , 
                   "compañerismo" : compañerismo}
        
        colegio[dni]["evaluaciones"].append(partido)

def pedir_bool(pregunta):
    while True:
        respuesta = input(f"{pregunta} (s/n): ").lower()
        if respuesta == 's':
            return True
        elif respuesta == 'n':
            return False
        else:
            print("Por favor, responda 's' para Sí o 'n' para No.")

def datos():

    dni = input("Ingrese el dni de quien quiere saber los datos: ")
    print(colegio[dni])

def menu():
    while True:
        print("MENÚ PARA PROGRAMA ARBITROS")
        print("1- Agregar juez")
        print("2- Agregar partidos")
        print("4- Mostrar datos")
        print("3- Salir")
        print("5- Agregar desempeño en cancha")

        opc = int(input("Ingrese la opcion que quiera realizar: "))

        if opc == 1:
            registro()
        elif opc == 2:
            designar()
        elif opc == 4:
            datos()
        elif opc == 5: 
            desempeño()
        else:
            print("Saliendo...")
            break

menu()




