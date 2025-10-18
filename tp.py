#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import pandas as pd
import duckdb as dd
import numpy as np

#Establecimientos: Data frame de Establecimientos Educativos del padròn del 2022


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
            "Nivel inicial - Jardín de infantes" as jardin, Primario, Secundario,
            "Secundario - INET" as SecuInet, "SNU" as Snu, "SNU - INET" as SnuInet
            FROM Establecimientos;
          """

Establecimientos = dd.sql(elimino).df()

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
padron_pob_limpio = pd.DataFrame(columns=['Area', 'Edad', 'Casos'])
areas = []
edades = []
casos = []

area_actual = ""
for index, row in padron_poblacional.iterrows():
    primera_celda = str(row[1])
    if (pd.notnull(row[1])):
        primera_celda = primera_celda.strip()
        if ("AREA" in primera_celda):
            area_actual= primera_celda
        elif (primera_celda.isdigit()):
            areas.append(area_actual)
            edades.append(primera_celda)
            casos.append(str(row[2]).strip())

padron_pob_limpio['Area'] = areas
padron_pob_limpio['Edad'] = edades
padron_pob_limpio['Casos'] = casos

#%%

consultaCantNivelesPorDepto =    """
                            SELECT Provincia, Departamento, COUNT(Maternal) as Maternales, 
                            COUNT(jardin) as Jardines, COUNT(Primario) as Primarias,
                            COUNT(Secundario) as Secundarias, COUNT(SecuInet) as SecuInets,
                            COUNT(Snu) as Snus, COUNT(SnuInet) as SnuInets
                            FROM Establecimientos
                            WHERE Maternal = '1' OR Jardin = '1' OR Primario = '1' OR
                            Secundario = '1' OR SecuInet = '1' OR Snu = '1'
                            OR SnuInet = '1'
                            GROUP BY Departamento, Provincia;
                        """
df_EstablecimientosPorDepartamento = dd.sql(consultaCantNivelesPorDepto).df()

# print(df_EstablecimientosPorDepartamento)


# consultaVerificoDepartamentos = """
#                                     SELECT COUNT(DISTINCT Departamento)
#                                     FROM df_EstablecimientosPorDepartamento;
#                                 """
# verifico = dd.sql(consultaVerificoDepartamentos).df()

# print(verifico)



