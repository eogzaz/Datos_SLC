import pandas as pd
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

def calc_envolvente(df, bin_width=0.1):
    alpha = df['Fase'].copy().to_numpy()
    m_red = df['Magn_redu'].copy().to_numpy()
    
    brightest_alpha = []
    brightest_mag = []

    for a_min in np.arange(min(alpha), max(alpha), bin_width):
        mask = (alpha >= a_min) & (alpha < a_min + bin_width)
        if np.any(mask):
            idx = np.argmin(m_red[mask])  # punto más brillante
            brightest_alpha.append(alpha[mask][idx])
            brightest_mag.append(m_red[mask][idx])

    brightest_alpha = np.array(brightest_alpha)
    brightest_mag = np.array(brightest_mag)

    slope, intercept, r_value, _, _ = linregress(brightest_alpha, brightest_mag)
    r2 = r_value**2

    return [slope, intercept,brightest_alpha,brightest_mag]

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

