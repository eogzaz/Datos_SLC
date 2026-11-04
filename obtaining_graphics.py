import pandas as pd
import polars as pl
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress


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



 # Función de filtrado
def fase_menor_5(data_sin_editar,desde=5):
  data = data_sin_editar.copy()
  fase = data['Fase'].to_numpy()
  data['Fase'] = np.where(fase < desde, np.nan, fase)
  return data.dropna().reset_index(drop=True)

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



def grafica_fase(df, alpha_max,magn_max,title='none', familia='none', recta_pendiente=False, pendiente_param = [],limites=np.array([0,35,17,10])):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.plot(df['Fase'], df['Magn_redu'].astype(float), 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)
    
    if recta_pendiente==True:
        x = np.linspace(0,40,100)
        pendiente = pendiente_param[0]
        intercep = pendiente_param[1]
        y = intercep + pendiente*x
        ax.plot(x,y,'r-', linewidth=3, label=f'm(1,1,0) = {round(intercep,2)} + {pendiente:.2}α')
        #ax.plot(alpha_max,magn_max,'o', markerfacecolor='red', markeredgecolor='red', markersize=5)
        ax.legend()
    
    if not familia==None:
        ax.set_title(f'{title} ({familia}) - Curva de Fase')
    else:
        ax.set_title(f'{title} - Curva de Fase')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('α [°]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

def calc_envolvente(df):
    df_fase = df[['Fase', 'Magn_redu']].copy()
    df_fase_ord = df_fase.sort_values('Fase').copy()
    #mean_magn_redu = df_fase_ord['Magn_redu'].mean()
    #df_fase_ord['diff_magn_redu_mean'] = df_fase_ord['Magn_redu'] - mean_magn_redu
    #std_magn_redu = df_fase_ord['Magn_redu'].std()
    #df_fase_fil = df_fase_ord[df_fase_ord['diff_magn_redu_mean'] <= (3 * std_magn_redu)].copy()

    # 3. Percentile Calculation and Joining
    df_with_interval = df_fase_ord.copy()
    df_with_interval['Fase_interval'] = df_with_interval['Fase'].astype(int)

    percentile_10_per_interval = df_with_interval.groupby('Fase_interval')['Magn_redu'].quantile(0.1, interpolation='linear').reset_index(name='p10_magn_redu')

    df_joined = df_with_interval.merge(
        percentile_10_per_interval,
        on='Fase_interval',
        how='left'
    )

    df_filtered_by_percentile = df_joined[df_joined['Magn_redu'] <= df_joined['p10_magn_redu']].copy()

    df_mean_below_p10 = df_filtered_by_percentile.groupby('Fase_interval')['Magn_redu'].mean().reset_index(name='mean_magn_redu_below_p10').sort_values('Fase_interval')

    # 4. Linear Regression
    fase_interval_p10 = df_mean_below_p10['Fase_interval'].to_numpy()
    mean_magn_redu_p10 = df_mean_below_p10['mean_magn_redu_below_p10'].to_numpy()

    slope, intercept, r_value, p_value, std_err = stats.linregress(fase_interval_p10, mean_magn_redu_p10)

    # 5. Flattening the Data
    #df_plano = df_fase_fil.copy()
    #df_plano['Magn_redu_plano'] = df_plano['Magn_redu'] - slope * df_plano['Fase'] - intercept

    return slope, intercept, fase_interval_p10, mean_magn_redu_p10, r_value, p_value, std_err

def grafica_fase_con_envolvente(df, fase_interval_p10, mean_magn_redu_p10, slope, intercept, title='none', familia='none', limites=np.array([0,35,17,10])):         
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.plot(df['Fase'], df['Magn_redu'].astype(float), 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)
    ax.plot(fase_interval_p10, mean_magn_redu_p10, 'o', markerfacecolor='red', markeredgecolor='red', markersize=4)

    x = np.linspace(xmin, xmax, 100)
    y = intercept + slope * x
    ax.plot(x, y, 'r-', linewidth=3, label=f'm(1,1,0) = {round(intercept,2)} + {slope:.2}α')
    ax.legend()

    if not familia==None:
        ax.set_title(f'{title} ({familia}) - Curva de Fase con Envolvente')
    else:
        ax.set_title(f'{title} - Curva de Fase con Envolvente')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('α [°]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig  

def grafica_envolvente(fase_interval_p10, mean_magn_redu_p10, slope, intercept, title='none', familia='none', limites=np.array([0,35,17,10])):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    fig, ax = plt.subplots(figsize=(6, 5))

    ax.plot(fase_interval_p10, mean_magn_redu_p10, 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)

    x = np.linspace(xmin, xmax, 100)
    y = intercept + slope * x
    ax.plot(x, y, 'r-', linewidth=3, label=f'm(1,1,0) = {round(intercept,2)} + {slope:.2}α')
    ax.legend()

    if not familia==None:
        ax.set_title(f'{title} ({familia}) - Envolvente')
    else:
        ax.set_title(f'{title} - Envolvente')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('α [°]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig


def grafica_SLC(df, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
  xmin = float(limites[0])
  xmax = float(limites[1])
  ymin = float(limites[2]) 
  ymax = float(limites[3]) 

  fig, ax = plt.subplots(figsize=(6, 5))

  # Second plot (SLC)
  ax.plot(df['t-Tq'], df['Magn_redu'].astype(float), 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)
  
  if not intercepto==None:
    x=np.linspace(xmin,xmax,100)
    y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
    ax.plot(x,y,'r-', linewidth=3)

  ax.set_ylim(ymin, ymax)
  ax.set_xlim(xmin, xmax)

  if not familia==None:
    ax.set_title(f'{title} ({familia}) - SLC')
  else:
    ax.set_title(f'{title}  - SLC')

  ax.set_xlabel('t-Tq [días]')
  ax.set_ylabel('m(1,1,α)')
  ax.tick_params(direction='in')
  ax.grid()

  return fig

def grafica_SLC_corr(df, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
  xmin = float(limites[0])
  xmax = float(limites[1])
  ymin = float(limites[2]) 
  ymax = float(limites[3]) 

  fig, ax = plt.subplots(figsize=(6, 5))

  # Second plot (SLC)
  ax.plot(df['t-Tq'], df['Magn_Corr_Fase'].astype(float), 'o', markerfacecolor='cyan', markeredgecolor='blue', markersize=2)
 
  if not intercepto==None:
    x=np.linspace(xmin,xmax,100)
    y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
    ax.plot(x,y,'r-', linewidth=3)
 
  ax.set_ylim(ymin, ymax)
  ax.set_xlim(xmin, xmax)

  if not familia==None:
    ax.set_title(f'{title} ({familia}) - SLC corr Fase')
  else:
    ax.set_title(f'{title}  - SLC corr Fase')

  ax.set_xlabel('t-Tq [días]')
  ax.set_ylabel('m(1,1,0)')
  ax.tick_params(direction='in')
  ax.grid()

  return fig


def clasificacion_periodos(df,periodo, perihelio):
    df['Date']= [str(df['Anio'][i])+' '+str(df['Mes'][i])+' '+str(df['Dia'][i]) for i in range(len(df))]
    df['JD'] = df['Date'].apply(Date_to_julian)

    num_periodos = int((max(df['JD'])-min(df['JD']))/periodo)+3
    if max(df['JD'])<perihelio:
        limites_entre_periodos = np.ones(num_periodos)
        for i in range(0,num_periodos):
            limites_entre_periodos[i]= perihelio-periodo*i
    else:
        limites_entre_periodos = np.ones(num_periodos)
        for i in range(num_periodos):
            limites_entre_periodos[i]= perihelio-periodo*(i-1)
            
    dic = {}
    for j in range(1,num_periodos):
        array1=df['JD']<limites_entre_periodos[j-1]
        array2=limites_entre_periodos[j]<=df['JD']
        boleanos = [int(a) * int(b) for a, b in zip(array1, array2)]
        b=pd.Series([bool(i) for i in boleanos])
        dic[j-1]=df.where(b).dropna()

    return dic, limites_entre_periodos

def grafica_fase_colores(dic, title='none', familia='none', recta_pendiente=False, pendiente_param = [],limites=np.array([0,35,17,10])):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    marcadores = ['o', 's', '^', 'D', 'v', '*', 'P', 'X']
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['Fase'],dic[i]['Magn_redu'],marcadores[i % len(marcadores)],markersize=5)

    if recta_pendiente==True:
        x = np.linspace(0,40,100)
        pendiente = pendiente_param[0]
        intercep = pendiente_param[1]
        y = intercep + pendiente*x
        ax.plot(x,y,'r-', linewidth=3, label=f'm(1,1,0) = {round(intercep,2)} + {pendiente:.2}α')
        ax.legend()
    
    if not familia==None:
        ax.set_title(f'{title} ({familia}) - Curva de Fase')
    else:
        ax.set_title(f'{title} - Curva de Fase')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel('α [°]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

def SLC_colores(dic, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 
    
    marcadores = ['o', 's', '^', 'D', 'v', '*', 'P', 'X']
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['t-Tq'],dic[i]['Magn_redu'],marcadores[i % len(marcadores)],markersize=5)

    if not intercepto==None:
        x=np.linspace(xmin,xmax,100)
        y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
        ax.plot(x,y,'r-', linewidth=3)
   
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(xmin, xmax)

    if not familia==None:
        ax.set_title(f'{title} ({familia}) - SLC colores')
    else:
        ax.set_title(f'{title}  - SLC colores')

    ax.set_xlabel('t-Tq [días]')
    ax.set_ylabel('m(1,1,α)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

def SLC_colores_corr(dic, title='none', familia='none', intercepto=1, limites=np.array([-800,800,17,10]) ):
    xmin = float(limites[0])
    xmax = float(limites[1])
    ymin = float(limites[2]) 
    ymax = float(limites[3]) 

    marcadores = ['o', 's', '^', 'D', 'v', '*', 'P', 'X']
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['t-Tq'],dic[i]['Magn_Corr_Fase'],marcadores[i % len(marcadores)],markersize=5)

    x=np.linspace(xmin,xmax,100)
    y=np.ones_like(np.linspace(xmin,xmax,100))*intercepto
    ax.plot(x,y,'r-', linewidth=3)
   
    ax.set_ylim(ymin, ymax)
    ax.set_xlim(xmin, xmax)

    if not familia==None:
        ax.set_title(f'{title} ({familia}) - SLC corr Fase colores')
    else:
        ax.set_title(f'{title}  - SLC corr Fase colores')

    ax.set_xlabel('t-Tq [días]')
    ax.set_ylabel('m(1,1,0)')
    ax.tick_params(direction='in')
    ax.grid()

    return fig

