import streamlit as st
import os
import pandas as pd
import calendar
from datetime import datetime, timedelta
from openpyxl import load_workbook
from openpyxl.styles import Alignment


# Função para ajustar largura das colunas no Excel
def ajustar_largura_colunas_excel(caminho_arquivo):
    wb = load_workbook(caminho_arquivo)
    ws = wb.active
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column].width = adjusted_width
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal='center')
    wb.save(caminho_arquivo)



# Função para converter CSV em Excel
def csv_excel(input_csv, output_folder):
    try:
        dados_csv = pd.read_csv(input_csv)
        output_excel = os.path.join(output_folder, "ResultadosExcel.xlsx")
        dados_csv.to_excel(output_excel, index=False)
        return output_excel
    except Exception as e:
        st.error(f"Erro ao converter CSV para Excel: {str(e)}")
        return None
    


def analisar_conforto_termico(df_excel, ano=2025, verbose=True):
    CONFORT_MIN = 18 
    CONFORT_MAX = 29  
    INTERVALO_MINUTOS = 15  
    HORAS_POR_INTERVALO = INTERVALO_MINUTOS / 60  

    # Pré-processamento
    df = df_excel.copy()
    df.columns = df.columns.str.strip()

    if "Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)" in df.columns:
        df.drop(columns=["Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)"], inplace=True) # remove uma coluna desnecesssária para a análise de conforto térmico

    cols_temp = [(col.split(':')[0], col) for col in df.columns if "Mean Air Temperature" in col]

    # cria as colunas "data" e "hora" a partir da coluna "Date/Time"
    def formatar_data_hora(df):
        date = []
        hour = []
        for value in df['Date/Time'].astype(str):
            parts = value.strip().split()
            if len(parts) == 2:
                date_str, hour_str = parts
            else:
                date_str = parts[0]
                hour_str = '00:00:00'
            day, month = map(int, date_str.split('/'))
            data_formatada = f"{day:02d}/{month:02d}/{ano}"
            hora_formatada = hour_str
            date.append(data_formatada)
            hour.append(hora_formatada)
        df.drop(columns=['Date/Time'], inplace=True)
        df.insert(0, "Hora", hour)
        df.insert(0, "Data", date)
        return df

    # Função para formatar as colunas de data e hora e criar a coluna DateTime no padrão datetime
    def formatar_para_datetime(dataframe):
        datas_reais = []
        for _, row in dataframe.iterrows():
            try:
                if pd.isna(row['Data']) or pd.isna(row['Hora']):
                    raise ValueError("Valores ausentes em 'Data' ou 'Hora'.")
                date_str = row['Data']
                time_str = row['Hora']
                day, month, year = map(int, date_str.split('/'))
                base_date = datetime(year=year, month=month, day=day)
                if time_str.startswith('24:'):
                    base_date += timedelta(days=1)
                    time_str = '00' + time_str[2:]
                hora, minuto, segundo = map(int, time_str.split(':'))
                data_certa = datetime(base_date.year, base_date.month, base_date.day, hora, minuto, segundo)
                datas_reais.append(pd.Timestamp(data_certa))
            except:
                datas_reais.append(pd.NaT)
        return datas_reais

    def processar_dados_temporais(df, cols_temp):
        for _, col in cols_temp:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['DateTime'] = formatar_para_datetime(df)
        df = df[df['DateTime'].notna()].copy()
        if df['DateTime'].empty:
            return df
        df['Month'] = df['DateTime'].dt.month
        df['Month_Name'] = df['DateTime'].dt.month_name()
        df['Hour'] = df['DateTime'].dt.hour
        df['Day'] = df['DateTime'].dt.day
        return df

    def calcular_metricas_conforto(data, temp_col):
        if data.empty:
            return {k: 0 for k in [
                'Total de Horas', 'Conforto (Dia)', 'Conforto (Noite)',
                'Total Conforto', 'Sem Conforto', '% Conforto', '% Sem Conforto']}
        total_horas = len(data) * HORAS_POR_INTERVALO
        periodo_dia = (data['Hour'] >= 6) & (data['Hour'] < 18)
        in_conforto = data[temp_col].between(CONFORT_MIN, CONFORT_MAX)
        conforto_dia = (periodo_dia & in_conforto).sum() * HORAS_POR_INTERVALO
        conforto_noite = ((~periodo_dia) & in_conforto).sum() * HORAS_POR_INTERVALO
        total_conforto = conforto_dia + conforto_noite

        # dicionário com as métricas calculadas (valores da tabela_conforto)
        return {
            'Total de Horas': round(total_horas, 2),
            'Conforto (Dia)': round(conforto_dia, 2),
            'Conforto (Noite)': round(conforto_noite, 2),
            'Total Conforto': round(total_conforto, 2),
            'Sem Conforto': round(total_horas - total_conforto, 2),
            '% Conforto': round((total_conforto / total_horas) * 100, 1),
            '% Sem Conforto': round(100 - ((total_conforto / total_horas) * 100), 1)
        }

    def gerar_relatorio_conforto(df, cols_temp):
        df = processar_dados_temporais(df, cols_temp)
        if df.empty:
            return pd.DataFrame()

        resultados = []
        for mes_num in range(1, 13):
            mes_nome = calendar.month_name[mes_num]
            dados_mes = df[df['Month'] == mes_num]
            for local, temp_col in cols_temp:
                if dados_mes.empty or temp_col not in dados_mes.columns:
                    metricas = {k: 0 for k in [
                        'Total de Horas', 'Conforto (Dia)', 'Conforto (Noite)',
                        'Total Conforto', 'Sem Conforto', '% Conforto', '% Sem Conforto']}
                else:
                    metricas = calcular_metricas_conforto(dados_mes, temp_col)
                resultados.append({'Mês': mes_nome, 'Local': local, **metricas})
        return pd.DataFrame(resultados)

    df = formatar_data_hora(df)
    return gerar_relatorio_conforto(df, cols_temp)