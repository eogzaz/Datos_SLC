import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from cleaning_data import *
from obtaining_data import *
from astropy.time import Time

#from data_cleansing import limpieza_obsevaciones, organizacion_df
import streamlit as st

@st.cache_data(show_spinner=False)
def obtencion_dataframe(asteroide, orbital_period, date_perihelion, object_type, fecha_inicial='1980 01 01', fecha_final='2025 07 12'):
  #Obtencion de datos obsrvacionales MPC
  df_obs = limpieza_obsevaciones(asteroide,DATA().get_observations(asteroide)[['obsTime', 'mag', 'band']],fecha_inicial,fecha_final)

  #Obtención efemerides
  df_efeme = DATA().get_ephemerides(asteroide,fecha_inicial,fecha_final,object_type)
  #df_efeme['Date JD'] = df_efeme['Date'].apply(lambda x: Time(x).jd)

  #dataframe total
  df_total=pd.merge(df_obs, df_efeme, left_on='Julian Day N', right_on='Date JD', how='inner')[['obsTime','Delta','r','Fase','Magn_obs']]

  if object_type=='Objeto Interestelar':
     df_total['t-Tq'] = df_total['obsTime'].apply(lambda x: -(date_perihelion-x).total_seconds() / 86400)
  else:
    df_total['t-Tq'] = df_total['obsTime'].apply(lambda x: Distancia_Perihelio(x, date_perihelion, orbital_period))

  df_total['Magn_redu'] = df_total['Magn_obs'].astype(float) - 5*np.log10(df_total['r']*df_total['Delta'])

  return organizacion_df(df_total)

def obtencion_dataframe_COBS(cometa, orbital_period, date_perihelion, object_type, fecha_inicial='1980 01 01', fecha_final='2025 07 12'):
  #Obtencion de datos obsrvacionales MPC
  df_obs = limpieza_obsevaciones_COBS(DATA().get_COBS_Observations(cometa),fecha_inicial,fecha_final)

  #Obtención efemerides
  df_efeme = DATA().get_ephemerides(cometa,fecha_inicial,fecha_final,object_type)

  #dataframe total
  df_total=pd.merge(df_obs, df_efeme, left_on='Julian Day N', right_on='Date JD', how='inner')[['obsTime','Delta','r','Fase','Magn_obs']]

  if object_type=='Objeto Interestelar':
     df_total['t-Tq'] = df_total['obsTime'].apply(lambda x: -(date_perihelion-x).total_seconds() / 86400)
  else:
    df_total['t-Tq'] = df_total['obsTime'].apply(lambda x: Distancia_Perihelio(x, date_perihelion, orbital_period))

  df_total['Magn_redu'] = df_total['Magn_obs'].astype(float) - 5*np.log10(df_total['r']*df_total['Delta'])

  return organizacion_df(df_total)


def promedio_corrido(df: pd.DataFrame, columna: str, ventana: int, nueva_columna: str = None) -> pd.DataFrame:
    """
    Calcula el promedio corrido (media móvil) de una columna de un DataFrame 
    y lo devuelve en una nueva columna en una copia del DataFrame original.

    Args:
        df (pd.DataFrame): DataFrame de entrada.
        columna (str): Nombre de la columna sobre la cual se calcula el promedio corrido.
        ventana (int): Tamaño de la ventana para el promedio corrido.
        nueva_columna (str, opcional): Nombre de la nueva columna. 
                                       Si no se especifica, será '<columna>_prom_corrido'.

    Returns:
        pd.DataFrame: Copia del DataFrame con la nueva columna añadida.
    """

    df['Magn_redu'] = df['Magn_redu'].rolling(window=ventana,min_periods=1).mean()
    return df
