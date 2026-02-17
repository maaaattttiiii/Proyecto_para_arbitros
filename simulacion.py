pagos_sucios = [
    {"nombre": "Juan Pérez", "monto": "$5000"},       # Tiene signo $
    {"nombre": "Ana Gomez", "monto": "3000"},         # Es texto, no número
    {"nombre": "Luis Silva", "monto": ""},            # ¡Está vacío!
    {"nombre": "Carlos Ruiz", "monto": 4500},         # Este está bien (es int)
    {"nombre": "Maria Sol", "monto": "2500.50"},      # Decimal como texto
    {"nombre": "Pedro A.", "monto": "Error de carga"} # Texto basura
]

def recorrer():
    total = 0 
    for i in pagos_sucios:
        try:
            dato = i["monto"]

            dato_limpio = str(dato).replace('$', '')

            num = float(dato_limpio)

            total += num
        except ValueError:
            print(f"Dato ignorado de {i['nombre']} (Valor inválido: '{i['monto']}')")
    print("-" * 30)
    print(f"el total a pagar es: ${total}")

recorrer()

            