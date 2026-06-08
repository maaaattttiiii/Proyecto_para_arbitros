# logic.py

def validar_reglas_negocio(datos):
    errores = []
    
    if datos['arbitro'] == "-- Seleccionar --" or datos['companero'] == "-- Seleccionar --":
        errores.append("Debes seleccionar Arbitro Principal y Compañero.")
    if datos['arbitro'] == datos['companero'] and datos['arbitro'] != "-- Seleccionar --":
        errores.append("El Principal y el Compañero no pueden ser la misma persona.")
    if datos['hubo_3er'] and (datos['tercer_juez'] == "-- Seleccionar --" or datos['tercer_juez'] in [datos['arbitro'], datos['companero']]):
        errores.append("Error en Tercer Juez (no seleccionado o duplicado).")
    
    if not datos['equipo_local'].strip() or not datos['equipo_visitante'].strip():
        errores.append("Debes ingresar el Equipo Local y el Equipo Visitante.")
    if not datos['cancha'].strip():
        errores.append("Debes ingresar la cancha o estadio donde se jugo.")
        
    if datos['categoria'] in ["Mosquitos", "Premini"] and (datos['hubo_3er'] or datos['hubo_ct']):
        errores.append(f"En categoria {datos['categoria']} no se designan Terceros Jueces ni CT.")
    if datos['categoria'] == "Superliga" and not datos['hubo_ct']:
        errores.append("Los partidos de Superliga requieren obligatoriamente un CT.")
        
    # Solo validamos la logica cardiaca si se activo la carga de datos fisicos
    if datos['hubo_fisico']:
        if datos['fc_pico'] < datos['fc_prom']:
            errores.append("Error logico: La FC Pico no puede ser menor a la FC Promedio.")
        if datos['distancia'] > 15.0:
            errores.append("Error logico: La distancia recorrida es inusualmente alta (mayor a 15 KM).")
        
    return errores

def calcular_puntaje_final(listas_notas):
    todas_las_notas = []
    for lista in listas_notas:
        todas_las_notas.extend(lista)
        
    notas_validas = [nota for nota in todas_las_notas if nota is not None]
    return sum(notas_validas) / len(notas_validas) if notas_validas else 0.0