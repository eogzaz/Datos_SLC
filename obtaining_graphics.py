import pandas as pd
import polars as pl
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from cleaning_data import Date_to_julian

 # Función de filtrado
def fase_menor_5(data_sin_editar,desde=5):
  data = data_sin_editar.copy()
  fase = data['Fase'].to_numpy()
  data['Fase'] = np.where(fase < desde, np.nan, fase)
  return data.dropna().reset_index(drop=True)

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

    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['Fase'],dic[i]['Magn_redu'],'o',markersize=2)
    
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
    
 
    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['t-Tq'],dic[i]['Magn_redu'],'o',markersize=2)

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

    fig, ax = plt.subplots(figsize=(6, 5))
    for i in range(len(dic)):
        ax.plot(dic[i]['t-Tq'],dic[i]['Magn_Corr_Fase'],'o',markersize=2)

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

