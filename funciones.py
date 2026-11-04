#librerias usadas, no modificar
import pandas as pd
import numpy as np
import requests
import xml.etree.ElementTree as ET
from astroquery.jplhorizons import Horizons
from astroquery.mpc import MPC
from bs4 import BeautifulSoup
from astropy.time import Time
import matplotlib.pyplot as plt
import os
from io import StringIO
import html, re
from datetime import datetime, timedelta


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

  return f'{year} {month} {int(day)}'


# --- Función auxiliar para obsTime ---
def parse_obs_time(val):
    if val is None or pd.isna(val):
        return pd.NaT
    val = val.strip()
    # Caso ISO
    try:
        return pd.to_datetime(val, errors="raise", utc=True)
    except Exception:
        pass
    # Caso YYYY-MM-DD.frac (día fraccionario)
    try:
        if "." in val and "-" in val:
            base, frac = val.split(".")
            frac = "0." + frac
            frac_day = float(frac)
            base_date = datetime.strptime(base, "%Y-%m-%d")
            return base_date + timedelta(days=frac_day)
    except Exception:
        pass
    return pd.NaT

# --- Saneador de XML ---
def _sanitize_xml(xml_string: str) -> str:
    s = xml_string.lstrip("\ufeff")
    s = html.unescape(s)
    s = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', s)  # control chars ilegales
    s = re.sub(r'&(?!#\d+;|#x[0-9A-Fa-f]+;|[A-Za-z][A-Za-z0-9]*;)', '&amp;', s)  # & sueltos
    return s

def observaciones_APIMPC(asteroide):
    url = "https://data.minorplanetcenter.net/api/get-obs"
    payload = {
        "desigs": [asteroide],
        "output_format": ["XML"]
    }

    response = requests.get(url, json=payload)
    if not response.ok:
        raise RuntimeError(f"Error {response.status_code}: {response.content.decode()}")

    # Aquí accedemos a la clave 'XML' del JSON de respuesta
    data = response.json()
    xml_string = data[0].get("XML", "")
    if not xml_string:
        raise RuntimeError(f"No se encontró contenido XML para '{asteroide}'")
   
    # --- Primer intento: versión simple (como tu original) ---
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError:
        # --- Si falla, aplicamos blindaje ---
        xml_string = _sanitize_xml(xml_string)
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError as e:
            fname = f"xml_error_{asteroide}.xml"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(xml_string)
            raise RuntimeError(f"XML inválido para {asteroide}: {e}. Guardado en {fname}")

    # Extraemos observaciones dentro del tag <optical>
    observaciones = []
    for obs in root.findall(".//optical"):
        datos = {child.tag: child.text for child in obs}
        observaciones.append(datos)

    df = pd.DataFrame(observaciones)

    # Manejo robusto de fechas
    if "obsTime" in df.columns:
        df["obsTime"] = df["obsTime"].apply(parse_obs_time)

    return df[['obsTime','mag','band']]

def efemerides_API(asteroide, fecha_inicial, fecha_final):
  url = "https://ssd.jpl.nasa.gov/api/horizons_file.api"

  # Comandos estilo archivo .api
  horizons_input = f"""
  !$$SOF
  COMMAND='{asteroide};'
  OBJ_DATA='YES'
  MAKE_EPHEM='YES'
  TABLE_TYPE='OBSERVER'
  CENTER='500@399'
  START_TIME='{fecha_inicial}'
  STOP_TIME='{fecha_final}'
  STEP_SIZE='1 d'
  QUANTITIES='1,19,20,43'
  !$$EOF
  """

  # Enviar como parámetro 'input'
  response = requests.post(url, data={'input': horizons_input})
  data = response.json()

  # Paso 3: Extraer el contenido plano del resultado
  raw_result = data["result"]
  start_idx = raw_result.find('$$SOE')+6
  end_idx = raw_result.find('$$EOE')
  lines = raw_result[start_idx:end_idx].splitlines()

  date, delta, r, alpha = [], [], [], []
  for line in lines:
    date  = np.append(date, line[1:12].strip())
    delta = np.append(delta, float(line[76:93].strip()))
    r     = np.append(r, float(line[48:63].strip()))
    alpha = np.append(alpha, float(line[108:115].strip()))

  efe = pd.DataFrame({'Date':date,'Date JD': [Date_to_julian(i) for i in date],'Delta':delta,'r':r,'fase':alpha})

  return efe


def periodo_fecha_perihelio(asteroide):
    datos = MPC.query_object('asteroid',number=asteroide,return_fields='period,perihelion_date,perihelion_date_jd')[0]
    periodo = float(datos['period'])*365.25
    fecha_perihelio = float(datos['perihelion_date_jd'])
    return periodo, fecha_perihelio

def Correccion_Banda(df):
  Correcciones={'V':0,
                'R':0.4,
                'G':0.28,
                'C':0.4,
                'r':0.14,
                'g':-0.35,
                'c':-0.05,
                'o':0.33,
                'w':-0.13,
                'i':0.32,
                'v':0,
                'Vj':0,
                'Rc':0.4,
                'Sg':-0.35,
                'Sr':0.14,
                'Si':0.32,
                'Pg':-0.35,
                'Pr':0.14,
                'Pi':0.32,
                'Pw':-0.13,
                'Ao':0.33,
                'Ac':-0.05,
                ''  :np.nan, # -0.8,
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
                'Gb':np.nan,
                'Gr':np.nan,
                'N':np.nan,
                'T':np.nan,
                }
  
  magn_con_Banda = df['mag'].copy()
  #Corrección estándar para convertir una magnitud en cualquier banda a banda V
  for i in range(len(df)):
    for j in range(len(Correcciones)):
      if df['band'].iloc[i]==list(Correcciones.keys())[j]:
        magn_con_Banda.iloc[i]=float(df['mag'].iloc[i])+list(Correcciones.values())[j]
    
    if pd.isna(df['band'].iloc[i]):
      magn_con_Banda.iloc[i]=np.nan


  df['Magn corregiada a banda V'] = magn_con_Banda
  df=df.dropna().reset_index(drop=True)

  return df

def Distancia_Perihelio(asteroide, df_obs,periodo,fecha_perihelio):
  def condicion(fecha,period=periodo):
    if (fecha_perihelio-fecha)%period >= period/2:
        distacia_al_perihelio=period-((fecha_perihelio-fecha)%period)
    else:
        distacia_al_perihelio=-((fecha_perihelio-fecha)%period)
    return round(distacia_al_perihelio)

  df_obs['Distancia_Perihelio'] = df_obs['Julian Day'].apply(condicion)
  return df_obs

def limpieza_obsevaciones(asteroide,df_obs_sin_limpiar, fecha_inicial, fecha_final):
  #Eliminar filas con almenos un NaN en la columna Magn y seleccion de las columnas que se van a usar
  df_obs_sin_nan= df_obs_sin_limpiar.dropna(subset=['mag'])[['obsTime','mag','band']].reset_index(drop=True)

  #Seleccion de solo las observaciones en Filtro V y R, y cambio de formato de fecha
  df_obs = Correccion_Banda(df_obs_sin_nan)

  #Agrego columna con dia juliano
  df_obs['Julian Day']=df_obs['obsTime'].apply(Date_to_julian)
  df_obs['Julian Day N']=df_obs['obsTime'].apply(Date_to_julian_N)

  #Rango de fechas
  df_obs=df_obs[(df_obs['Julian Day']>=Date_to_julian(fecha_inicial)) & (df_obs['Julian Day']<=Date_to_julian(fecha_final))]

  df_obs=df_obs.reset_index(drop=True)
    
  periodo, fecha_al_perihelio = periodo_fecha_perihelio(asteroide)
  df_obs=Distancia_Perihelio(asteroide, df_obs,periodo,fecha_al_perihelio)

  return df_obs

def organizacion_df(df):
  df.insert(1, 'Año', df['obsTime'].apply(lambda x: x.year))
  df.insert(2, 'Mes', df['obsTime'].apply(lambda x: x.month))
  df.insert(3, 'Dia', df['obsTime'].apply(lambda d:  round(d.day + d.hour / 24.0 + d.minute / (24.0 * 60.0) + d.second / (24.0 * 60.0 * 60.0) + d.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0),2)))
  df.drop(columns=['obsTime'], inplace=True)

  df['Delta'] = df['Delta'].apply(lambda x: round(x,2))
  df['r'] = df['r'].apply(lambda x: round(x,2))
  df['fase'] = df['fase'].apply(lambda x: round(x,2))
  df['Magn'] = df['Magn'].apply(lambda x: round(float(x),2))
  df['Magn_abs'] = df['Magn_abs'].apply(lambda x: round(x,2))

  return df

def obtencion_dataframe(asteroide, fecha_inicial='1980 01 01', fecha_final='2025 07 12'):
  #Obtencion de datos obsrvacionales MPC
  df_obs = limpieza_obsevaciones(asteroide,observaciones_APIMPC(asteroide),fecha_inicial,fecha_final)

  #Obtención efemerides
  df_efeme = efemerides_API(asteroide,fecha_inicial,fecha_final)

  #dataframe total
  df_total=pd.merge(df_obs, df_efeme, left_on='Julian Day N', right_on='Date JD', how='inner')[['obsTime','Distancia_Perihelio','Delta','r','fase','Magn corregiada a banda V']]
  df_total = df_total.rename(columns={'Magn corregiada a banda V': 'Magn'})
  df_total['Magn_abs'] = df_total['Magn'].astype(float) - 5*np.log10(df_total['r']*df_total['Delta'])

  return organizacion_df(df_total)
