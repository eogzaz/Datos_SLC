import pandas as pd
import numpy as np
from astropy.time import Time

# Ver el documento "C:\Users\Asus\Desktop\APP_MPC_agrupados_version3\Corrección a la banda V programa.docx"
def Correccion_Banda(df):
  Correcciones={'V':0,'R':0.4,'G':0.28,'C':0.4,'r':0.14,'g':-0.35,'c':-0.05,'o':0.33,'w':-0.13,'i':0.32,'v':0,'Vj':0,
                'Rc':0.4,'Sg':-0.35,'Sr':0.14,'Si':0.32,'Pg':-0.35,'Pr':0.14,'Pi':0.32,'Pw':-0.13,'Ao':0.33,'Ac':-0.05,
                ''  :np.nan,#-0.8,
                'U' :np.nan, # -1.3,
                'u' :np.nan, # 2.5,
                'B' :np.nan, # -0,
                'I' :np.nan, # 0.8,
                'J' :np.nan, # 1.2,
                'H' :np.nan, # 1.4,
                'K' :np.nan, # 1.7,
                'W' :np.nan, # 0.4,
                'Y' :np.nan, # 0.7,
                'z' :np.nan, # 0.26,
                'y' :np.nan, # 0.32,
                'Lu':np.nan, #2.5,
                'Lg':np.nan, #-0.35,
                'Lr':np.nan, #0.14,
                'Lz':np.nan, #0.26,
                'Ly':np.nan, #0.32,
                'VR':np.nan, #0,
                'Ic':np.nan, #0.8,
                'Bj':np.nan, #-0.8,
                'Uj':np.nan, #-1.3,
                'Sz':np.nan, #0.26,
                'Pz':np.nan, #0.26,
                'Py':np.nan, #0.32,
                'Gb':np.nan,'Gr':np.nan,'N':np.nan,'T':np.nan,
                }
  
  magn_con_Banda = df['mag'].copy()
  #Corrección estándar para convertir una magnitud en cualquier banda a banda V
  for i in range(len(df)):
    for j in range(len(Correcciones)):
      if df['band'].iloc[i]==list(Correcciones.keys())[j]:
        magn_con_Banda.iloc[i]=float(df['mag'].iloc[i])+list(Correcciones.values())[j]
    
    if pd.isna(df['band'].iloc[i]):
      magn_con_Banda.iloc[i]=np.nan


  df['Magn_obs'] = magn_con_Banda
  df=df.dropna().reset_index(drop=True)

  return df

def Distancia_Perihelio1(df_obs,periodo,fecha_perihelio):
  def condicion(fecha,period=periodo):
    if (fecha_perihelio-fecha)%period >= period/2:
        distacia_al_perihelio=period-((fecha_perihelio-fecha)%period)
    else:
        distacia_al_perihelio=-((fecha_perihelio-fecha)%period)
    return round(distacia_al_perihelio)

  df_obs['t-Tq'] = df_obs['Julian Day'].apply(condicion)
  return df_obs

def Distancia_Perihelio(date, date_perihelion, period):
  if ((date_perihelion-date).total_seconds() / 86400)%period >= period/2:
      distacia_al_perihelio=period-(((date_perihelion-date).total_seconds() / 86400)%period)
  else:
      distacia_al_perihelio=-(((date_perihelion-date).total_seconds() / 86400)%period)
  return round(distacia_al_perihelio,2)  

import pandas as pd

#De fecha a día juliano
def Date_to_julian(d):
    # Handle pandas Timestamp object if passed
    if isinstance(d, pd.Timestamp):
        year = d.year
        month = d.month
        day_with_fraction = d.day + d.hour / 24.0 + d.minute / (24.0 * 60.0) + d.second / (24.0 * 60.0 * 60.0) + d.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
    # Handle 'YYYY-Mon-DD' string format
    elif isinstance(d, str) and '-' in d:
        date_obj = pd.to_datetime(d)
        year = date_obj.year
        month = date_obj.month
        day_with_fraction = date_obj.day + date_obj.hour / 24.0 + date_obj.minute / (24.0 * 60.0) + date_obj.second / (24.0 * 60.0 * 60.0) + date_obj.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
    else: # Assume original string format if not a Timestamp or 'YYYY-Mon-DD'
        year, month, day_with_fraction = d.split()
        year = int(year)
        month = int(month)
        day_with_fraction = float(day_with_fraction)

    day = int(day_with_fraction)
    fraction_of_day = day_with_fraction - day
    if month <= 2:
        year -= 1
        month += 12
    A = year // 100
    B = 2 - A + A // 4
    jd = int(365.25 * (year + 4716)) \
       + int(30.6001 * (month + 1)) \
         + day + B - 1524.5 + fraction_of_day
    return jd

#Dia juliano sin sin fraccion de dia
def Date_to_julian_N(d):
  return int(Date_to_julian(d))+.5

#De día juliano a fecha
def julian_to_date(jd):
  jd = jd + 0.5 # Sumamos 0.5 para que el inicio del día sea a medianoche

  Z = int(jd)
  F = jd - Z

  alpha = int((Z - 1867216.25)/36524.25)
  A = Z + 1 + alpha - int(alpha/4)

  B = A + 1524
  C = int((B - 122.1)/365.25)
  D = int(365.25 * C)
  E = int((B - D)/30.6001)

  day = B - D - int(30.6001 * E) + F

  if E < 14:
    month = E - 1
  else:
    month = E - 13

  if month > 2:
    year = C - 4716
  else:
    year = C - 4715

  # Convertir el día con fracción a horas, minutos, segundos y microsegundos
  fraction_of_day = day - int(day)
  hour = int(fraction_of_day * 24)
  minute = int((fraction_of_day * 24 - hour) * 60)
  second = int(((fraction_of_day * 24 - hour) * 60 - minute) * 60)
  microsecond = int(((((fraction_of_day * 24 - hour) * 60 - minute) * 60 - second) * 1000000))

  return f'{year}/{month}/{int(day)}'


def limpieza_obsevaciones(asteroide,df_obs_sin_limpiar, fecha_inicial, fecha_final):
  #Eliminar filas con almenos un NaN en la columna Magn y seleccion de las columnas que se van a usar
  df_obs_sin_nan= df_obs_sin_limpiar.dropna(subset=['mag'])[['obsTime','mag','band']].reset_index(drop=True)

  #Seleccion de solo las observaciones en Filtro V y R, y cambio de formato de fecha
  df_obs = Correccion_Banda(df_obs_sin_nan)

  #Agrego columna con dia juliano
  df_obs['Julian Day']=df_obs['obsTime'].apply(lambda x: Time(x).jd)
  df_obs['Julian Day N']=df_obs['obsTime'].apply(Date_to_julian_N)



  #Rango de fechas
  df_obs=df_obs[(df_obs['Julian Day']>=Date_to_julian(fecha_inicial)) & (df_obs['Julian Day']<=Date_to_julian(fecha_final))]

  df_obs=df_obs.reset_index(drop=True)
    
  #periodo, fecha_al_perihelio = periodo_fecha_perihelio(asteroide)
  #df_obs=Distancia_Perihelio(df_obs,periodo,fecha_al_perihelio)

  return df_obs

def limpieza_obsevaciones_COBS(df_obs_sin_limpiar, fecha_inicial, fecha_final):


  #Seleccion de solo las observaciones en Filtro V y R, y cambio de formato de fecha
  df_obs = df_obs_sin_limpiar.copy()

  #Agrego columna con dia juliano
  df_obs['Julian Day']=df_obs['obsTime'].apply(lambda x: Time(x).jd)
  df_obs['Julian Day N']=df_obs['obsTime'].apply(Date_to_julian_N)



  #Rango de fechas
  df_obs=df_obs[(df_obs['Julian Day']>=Date_to_julian(fecha_inicial)) & (df_obs['Julian Day']<=Date_to_julian(fecha_final))]

  df_obs=df_obs.reset_index(drop=True)

  return df_obs



def organizacion_df(df):
  df.insert(1, 'Anio', df['obsTime'].apply(lambda x: x.year))
  df.insert(2, 'Mes', df['obsTime'].apply(lambda x: x.month))
  df.insert(3, 'Dia', df['obsTime'].apply(lambda d:  round(d.day + d.hour / 24.0 + d.minute / (24.0 * 60.0) + d.second / (24.0 * 60.0 * 60.0) + d.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0),2)))
  df.drop(columns=['obsTime'], inplace=True)

  df['t-Tq'] = df['t-Tq'].apply(lambda x: round(x,2))
  df['Delta'] = df['Delta'].apply(lambda x: round(x,2))
  df['r'] = df['r'].apply(lambda x: round(x,2))
  df['Fase'] = df['Fase'].apply(lambda x: round(x,2))
  df['Magn_obs'] = df['Magn_obs'].apply(lambda x: round(float(x),2))
  df['Magn_redu'] = df['Magn_redu'].apply(lambda x: round(x,2))

  return df

