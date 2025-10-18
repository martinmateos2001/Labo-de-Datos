#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%


import pandas as pd
import duckdb as dd
import numpy as np

#%%Establecimientos: Data frame de Establecimientos Educativos del padròn del 2022


columnas_ee = 'A:C,L,N,U:AA'
"""
A - Jurisdiccion
B - Cueanexo
C - Nombre
L - Departamento
N - Común
U - Jardin maternal
V - Jardin de infantes
W - Primario
X - Secundario
Y - Secundario - INET
Z - SNU
AA - SNU - INET
"""


Establecimientos = pd.read_excel("2022_padron_oficial_establecimientos_educativos.xlsx", 
                                 skiprows=6, usecols= columnas_ee)

#Eliminamos los establecimientos que no son comunes
consultaSoloComunes = """
                      SELECT *
                      FROM Establecimientos
                      WHERE "Común" = '1';

                      """

Establecimientos = dd.sql(consultaSoloComunes).df()

#Eliminamos Cueanexo
elimino = """
            SELECT Jurisdicción as Provincia, Departamento, "Nivel inicial - Jardín maternal" as Maternal,
            "Nivel inicial - Jardín de infantes" as Jardin, Primario, Secundario,
            "Secundario - INET" as SecuInet, "SNU" as Snu, "SNU - INET" as SnuInet
            FROM Establecimientos;
          """

Establecimientos = dd.sql(elimino).df()

#%% Buscamos la cantidad de establecimientos que hay de cada nivel

def consultarCantNivelesPorDepto(nivel:str, nombreDelCount:str):
    consulta =  f"""
                   SELECT Provincia, Departamento, COUNT({nivel}) as {nombreDelCount}
                   FROM Establecimientos
                   WHERE {nivel} = '1'
                   GROUP BY Departamento, Provincia;
                   """
    return dd.sql(consulta).df()

cant_maternales_depto = consultarCantNivelesPorDepto('Maternal', 'Maternales')
cant_jardin_depto = consultarCantNivelesPorDepto('Jardin', 'Jardines')
cant_primaria_depto = consultarCantNivelesPorDepto('Primario', 'Primarios')
cant_jardin_depto = consultarCantNivelesPorDepto('Secundario', 'Secundarios')

                   
#%%padron_poblacional = Datos de poblacion por departamento

padron_poblacional = pd.read_excel("padron_poblacion.xlsX", skiprows=12, header=None)

#las ultimas 4 filas no sirven     
f_malas = []   
i:int() = len(padron_poblacional)-5
while(i < len(padron_poblacional)):     #las ultimas 4
    f_malas.append(i)
    i = i + 1

padron_poblacional.drop(index=f_malas, inplace=True, axis=0)

#Elimino la columna vacia y las filas vacias.
padron_poblacional.dropna(axis=1, how='all', inplace=True)
padron_poblacional.dropna(axis=0, how='all', inplace=True)

#%% padron limpio
padron_pob_limpio = pd.DataFrame(columns=['Cod_Departamento', 'Departamento', 'Edad', 'Casos'])
areas = []
deptos = []
edades = []
casos = []


def limpiarCodArea(area:str):
    sacar = 'AREA #'
    return area.replace(sacar, '')

area_actual = ""
depto_actual = ""
for index, row in padron_poblacional.iterrows():
    primera_celda = str(row[1])
    segunda_celda = str(row[2])
    if (pd.notnull(row[1])):
        primera_celda = primera_celda.strip()
        segunda_celda = segunda_celda.strip()
        if ("AREA" in primera_celda):
            area_actual= limpiarCodArea(primera_celda)
            depto_actual =  segunda_celda
        elif (primera_celda.isdigit()):
            areas.append(area_actual)
            deptos.append(depto_actual)
            edades.append(int(primera_celda))
            casos.append(int(segunda_celda))
        elif ("RESUMEN" in primera_celda):
            break

            

padron_pob_limpio['Cod_Departamento'] = areas
padron_pob_limpio['Departamento'] = deptos
padron_pob_limpio['Edad'] = edades
padron_pob_limpio['Casos'] = casos

#%% ESTABA PROBANDO: obtuve la poblacion total de cada departamento

consultaPoblacionTotalPorDeptos =   """
                                        SELECT Cod_Departamento, Departamento, SUM(Casos) as Poblacion_total,
                                        FROM padron_pob_limpio
                                        GROUP BY Cod_Departamento, Departamento;
                                    """
departamentos_poblacion_total = dd.sql(consultaPoblacionTotalPorDeptos).df()



#%% busco la cantidad de personas que hay respecto a cada nivel educativo
"""
maternal es [0, 2]
infantes es [3, 5]
primaria es [6, 12]
secundaria es [12, 18]
secuInet es [12, 19]
snu y snuInet > 18 años
"""
def consultarPobPorRangos(edad_minima:int, edad_maxima:int, nombre_poblacion:str) -> pd.DataFrame:
    consulta = f"""
                SELECT 
                    Cod_Departamento, Departamento, 
                    SUM(Casos) as {nombre_poblacion}
                FROM padron_pob_limpio
                WHERE Edad >= {edad_minima} AND Edad <= {edad_maxima}
                GROUP BY Cod_Departamento, Departamento;
                """
    return dd.sql(consulta).df()

#prueba = consultarPobPorRangos(0, 2, "asdf")


pob_maternal_depto = consultarPobPorRangos(0, 2, "Poblacion_Maternal")


pob_jardin_depto = consultarPobPorRangos(3, 5, "Poblacion_Jardin")

# Se solapan las poblaciones de 12 años
pob_primaria_depto = consultarPobPorRangos(6, 12, "Poblacion_Primaria")

pob_secu_depto = consultarPobPorRangos(12, 18, "Poblacion_Primaria")


# EN TERCIARIOS HAY QUE TOMAR DESICIONES (DEJO PENDIENTE)






