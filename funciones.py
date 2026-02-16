from fpdf import FPDF

def generar_reporte():
    print("\n--- GENERAR REPORTE PDF ---")
    dni = input("Ingrese el DNI del árbitro: ")
    
    if dni not in colegio:
        print(" Árbitro no encontrado.")
        return

    # Recuperamos los datos de la "Caja Grande"
    datos = colegio[dni]
    nombre_completo = f"{datos['nombre']} {datos['apellido']}"
    
    # --- CREACIÓN DEL PDF ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # 1. TÍTULO Y DATOS PERSONALES
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=f"Ficha Técnica: {nombre_completo}", ln=1, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"DNI: {dni} - Categoría: {datos['categoria']}", ln=1, align='C')
    pdf.ln(10) # Salto de línea

    # 2. SECCIÓN PAGOS (Diccionario)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Estado de Pagos (10%)", ln=1)
    pdf.set_font("Arial", size=12)
    
    if not datos['pagos']:
        pdf.cell(200, 10, txt="No hay registros de pago.", ln=1)
    else:
        # Recorremos el diccionario de pagos
        for fecha, estado in datos['pagos'].items():
            texto_estado = "A tiempo" if estado else " Debe/Tarde"
            pdf.cell(200, 10, txt=f"Fecha {fecha}: {texto_estado}", ln=1)
    
    pdf.ln(5)

    # 3. SECCIÓN PARTIDOS (Lista de Tuplas)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Historial de Partidos", ln=1)
    pdf.set_font("Arial", size=12)

    if not datos['partidos']:
        pdf.cell(200, 10, txt="No ha dirigido partidos aún.", ln=1)
    else:
        # Recorremos la lista de partidos
        # trabajo = (dia, mes , plata)
        total_ganado = 0
        for partido in datos['partidos']:
            dia, mes, plata = partido
            pdf.cell(200, 10, txt=f"- Dirigió el {dia}/{mes}. Ganancia: ${plata}", ln=1)
            total_ganado += float(plata) # Sumamos para el total
        
        pdf.set_font("Arial", style="B", size=12)
        pdf.cell(200, 10, txt=f"Total Ganado: ${total_ganado}", ln=1)

    pdf.ln(5)

    # 4. SECCIÓN DESEMPEÑO (Lista de Diccionarios)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Evaluaciones Técnicas (Categoría A)", ln=1)
    pdf.set_font("Arial", size=10) # Letra más chica para que entre todo

    if not datos['evaluaciones']:
        pdf.cell(200, 10, txt="Sin evaluaciones cargadas.", ln=1)
    else:
        for evaluacion in datos['evaluaciones']:
            # evaluacion es un diccionario pequeño
            fecha = f"{evaluacion['dia']}/{evaluacion['mes']}"
            resumen = f"Fecha: {fecha} | Ubicación: {'OK' if evaluacion['ubicacion'] else 'MAL'} | Señas: {'OK' if evaluacion['señas'] else 'MAL'}"
            pdf.cell(0, 10, txt=resumen, ln=1)

    # --- GUARDAR ARCHIVO ---
    nombre_archivo = f"Reporte_{datos['apellido']}_{dni}.pdf"
    pdf.output(nombre_archivo)
    print(f"\n PDF Generado con éxito: {nombre_archivo}")
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

def pagos(): 

    dni = input("Ingrese el dni del arbitro que quiere pagar")
    dia = input("Ingrese el dia: ")
    mes = input("Ingrese el mes: ")

    if dni in colegio:
        pago = pedir_bool(f"¿El arbitro {colegio[dni]['nombre']}, pagó el 10% de la siguiente fecha ({dia, mes})?")
        colegio[dni]["pagos"][f"{dia}/{mes}"] = pago

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
    if dni in colegio:

        print(colegio[dni])

def menu():
    while True:
        print("MENÚ PARA PROGRAMA ARBITROS")
        print("1- Agregar juez")
        print("2- Agregar partidos")
        print("4- Mostrar datos")
        print("3- Salir")
        print("5- Agregar desempeño en cancha")
        print("6- Registrar pago 10%")
        print("7- Generar reporte en PDF")

        opc = int(input("Ingrese la opcion que quiera realizar: "))

        if opc == 1:
            registro()
        elif opc == 2:
            designar()
        elif opc == 4:
            datos()
        elif opc == 5: 
            desempeño()
        elif opc == 6:
            pagos()
        elif opc == 7:
            generar_reporte()
        else:
            print("Saliendo...")
            break

menu()




