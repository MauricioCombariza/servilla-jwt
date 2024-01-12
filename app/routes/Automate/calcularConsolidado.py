import pandas as pd
import numpy as np
import os

def calcularConsolidado(archivo_base_rel, resultado_excel='consolidadoFinal.xlsx'):
    """
    Calcula precios finales a pagar por filial
    
    Retorna:
    - None
    """
    # Obtiene la ruta completa del archivo base
    ruta_completa_base = os.path.join(os.getcwd(), archivo_base_rel)

    # Verifica si el archivo base existe
    if not os.path.exists(ruta_completa_base):
        print(f"El archivo base '{ruta_completa_base}' no existe.")
        return

    # Lee el archivo base
    df = pd.read_excel(ruta_completa_base)
    df.set_index('ID', inplace=True)

    df_copy = df.copy()
    

    data = [103, 208, 209, 109, 211, 114, 515, 116, 118, 119, 122, 123, 324, 125, 131, 132, 133,
            134, 525, 136, 533, 534, 535, 536, 559, 447, 554, 557, 157, 558, 159, 560, 162, 373,
            580, 481, 486, 487, 488, 497, 595, 199, 198]
    ids_a_sumar = [703,708,709,710,711,714,715,716,718,719,722,723,724,725,731,732,733,734,735,
                   736,741,742,743,744,746,747,754,756,757,758,759,760,762,773,780,781,786,787,
                   788,797,795,798,998]

    for i in range(len(data)-1):
        id_actual = data[i]
        id_reclamo = ids_a_sumar[i]
        
        # Utilizar loc para evitar SettingWithCopyWarning
        df_copy.loc[id_actual, 'CUPONES'] += df_copy.loc[id_reclamo, 'CUPONES']
        df_copy.loc[id_actual, 'EDATEL'] += df_copy.loc[id_reclamo, 'EDATEL']
        df_copy.loc[id_actual, 'TIGO'] += df_copy.loc[id_reclamo, 'TIGO']
    
    # print(df_copy.index)
    
    df_resultado = df_copy
    bancolombia = [116, 118, 119, 560]
    df_resultado['UNE'] = np.where(
                                   df_resultado.index.isin(bancolombia), df_resultado['DATO_ENTIDAD'],
                                   np.where(df_resultado['CUPONES'] < 11, df_resultado['CUPONES'], 
                                   np.where(df_resultado['CUPONES'] < df_resultado['DATO_ENTIDAD'],
                                   df_resultado['CUPONES'] - (df_resultado['TIGO'] + df_resultado['EDATEL']),
                                   df_resultado['DATO_ENTIDAD'] - (df_resultado['TIGO'] + df_resultado['EDATEL']))))
    # Reordenar las columnas colocando 'CUPONES' al final
    columnas_ordenadas = [col for col in df_resultado.columns if col != 'CUPONES'] + ['CUPONES']
    df_resultado = df_resultado[columnas_ordenadas]
    # Reordenar las columnas colocando 'DATO_ENTIDAD' al final
    columnas_ordenadas = [col for col in df_resultado.columns if col != 'DATO_ENTIDAD'] + ['DATO_ENTIDAD']
    df_resultado = df_resultado[columnas_ordenadas]
    # Eliminar columnas temporales
    columnas_a_eliminar = [col for col in df_resultado.columns if col.endswith('_temporal')]
    df_resultado.drop(columns=columnas_a_eliminar, inplace=True)
    df_resultado['DIFERENCIA'] = df_resultado['CUPONES'] - df_resultado['DATO_ENTIDAD']
    df_resultado['TOTAL_EDATEL'] = df_resultado['EDATEL'] * df_resultado['TARIFA']
    df_resultado['TOTAL_TIGO'] = df_resultado['TIGO'] * df_resultado['TARIFA']
    df_resultado['TOTAL_UNE'] = df_resultado['UNE'] * df_resultado['TARIFA']
    df_resultado['TOTAL_FACTURADO'] = df_resultado['TOTAL_EDATEL'] + df_resultado['TOTAL_TIGO'] + df_resultado['TOTAL_UNE']

    df_resultado.to_excel(resultado_excel)
    print("Cálculado exitosamente !!")
