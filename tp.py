import pandas as pd
import duckdb as dd
import numpy as np

# Establecimientos: Data frame de Establecimientos Educativos del padròn del 2022


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


Establecimientos = pd.read_excel("/home/Estudiante/Descargas//2022_padron_oficial_establecimientos_educativos.xlsx", skiprows=6, usecols= columnas_ee)



consultaSoloComunes = """
                      SELECT *
                      FROM Establecimientos
                      WHERE "Común" = '1';

                      """

Establecimientos = dd.sql(consultaSoloComunes).df()

elimino = """
            SELECT Jurisdicción as Provincia, Departamento, "Nivel inicial - Jardín maternal" as maternal,
            "Nivel inicial - Jardín de infantes" as jardin, Primario, Secundario,
            "Secundario - INET" as SecuInet, "SNU" as Snu, "SNU - INET" as SnuInet
            FROM Establecimientos;
          """

Establecimientos = dd.sql(elimino).df()
print(Establecimientos)
