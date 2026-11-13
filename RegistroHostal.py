## REGISTRO DEL HOSTAL
## DATOS A TOMAR EN CUENTA:
## - Nombre del huésped
## - Fecha de llegada
## - Hora de llegada
## - Fecha de salida
## - Hora de salida
## - Número de habitación
## - Número de personas
## - HORA DE ATENCION -> DE: 8:00 A.M. HASTA 10:00 P.M.

import streamlit as st

HORA_MINIMA = 8
HORA_MAXIMA = 22
REGISTRO = []


def validar_hora_salida(hora_salida):
  ###  """Función única para validar que la hora de salida esté dentro del rango."""
    hora = int(hora_salida.split(":")[0]) if ":" in hora_salida else int(hora_salida)
    
    while hora < HORA_MINIMA or hora > HORA_MAXIMA:
        print("La hora de salida no puede ser mayor que las 10:00 P.M. ni menor a las 8:00 A.M. Por favor, ingrese una hora válida.")
        hora_salida = input("Ingrese la hora de salida (hh:mm): ")
        hora = int(hora_salida.split(":")[0]) if ":" in hora_salida else int(hora_salida)
        
    print("Hora de salida válida.")
    return hora_salida


def crear_huesped(garantia, nombre_huesped, fecha_llegada, hora_llegada, fecha_salida, hora_salida, numero_habitacion, numero_personas):
    huesped = {
        "Nombre": nombre_huesped,
        "Fecha de llegada": fecha_llegada,
        "Hora de llegada": hora_llegada,
        "Fecha de salida": fecha_salida,
        "Hora de salida": hora_salida,
        "Número de habitación": numero_habitacion,
        "Número de personas": numero_personas,
        "Garantia": garantia
    }
    return huesped


def registrar_huesped(huesped):
    REGISTRO.append(huesped)
    return huesped


def pedir_datos():
## donde se piden los datos
    garantia = input("Ingrese el tipo de garantía (efectivo): ")
    nombre_huesped = input("Ingrese el nombre del huésped: ")
    fecha_llegada = input("Ingrese la fecha de llegada (dd/mm/aaaa): ")
    hora_llegada = input("Ingrese la hora de llegada (hh:mm): ")
    fecha_salida = input("Ingrese la fecha de salida (dd/mm/aaaa): ")
    
    hora_salida_ingresada = input("Ingrese la hora de salida (hh:mm): ")
    hora_salida = validar_hora_salida(hora_salida_ingresada)
    
    numero_habitacion = input("Ingrese el número de habitación(C-X): ")
    numero_personas = input("Ingrese el número de personas: ")
    
    nuevo_huesped = crear_huesped(
        garantia, nombre_huesped, fecha_llegada, hora_llegada, 
        fecha_salida, hora_salida, numero_habitacion, numero_personas
    )
    registrar_huesped(nuevo_huesped)


# Ejecución
pedir_datos()
print(REGISTRO)