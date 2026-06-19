# logic.py

def validar_reglas_negocio(datos):
    errores = []
    if datos['hubo_fisico']:
        if datos['fc_pico'] < datos['fc_prom']:
            errores.append("Error lógico: La FC Pico no puede ser menor a la FC Promedio.")
        if datos['distancia'] > 15.0:
            errores.append("Error lógico: La distancia recorrida es inusualmente alta (mayor a 15 KM).")
    return errores

def calcular_puntaje_final(listas_notas):
    todas_las_notas = []
    for lista in listas_notas:
        todas_las_notas.extend(lista)
        
    notas_validas = [nota for nota in todas_las_notas if nota is not None]
    return sum(notas_validas) / len(notas_validas) if notas_validas else 0.0