import streamlit as st
import os
import subprocess
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment


def ajustar_largura_colunas_excel(caminho_arquivo):

    # Carregar o arquivo Excel com openpyxl
    wb = load_workbook(caminho_arquivo)
    ws = wb.active

    # Ajustar a largura das colunas
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Pega a letra da coluna (A, B, C, ...)
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        # Define a largura da coluna com base no conteúdo mais longo
        adjusted_width = (max_length + 2) * 1.2  
        ws.column_dimensions[column].width = adjusted_width

    # Centralizar o conteúdo das células 
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal='center')

    # Salvar o arquivo Excel com as alterações
    wb.save(caminho_arquivo)
    print(f"Largura das colunas ajustada e arquivo salvo em: {caminho_arquivo}")

# funçaõ para transformar csv em excel
def csv_excel(input_csv):
    try:
        # leitura do arquivo csv
        dados_csv = pd.read_csv(input_csv)

        # salvar com excel
        output_excel = os.path.join(OUTPUT_FOLDER, "ResultadosExcel.xlsx")
        dados_csv.to_excel(output_excel,index=False)

        return output_excel
    
    # indica erro 
    except Exception as e:
        st.error(f"Erro ao converter CSV para Excel: {str(e)}")
        return None # retorna arquivo vazio = false

# Configuração do Streamlit
st.title("🏠 EnergyPlus Simulation via Streamlit")

# Criar diretórios para uploads e saída
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Upload dos arquivos
idf_file = st.file_uploader("Envie o arquivo .idf", type=["idf"])
epw_file = st.file_uploader("Envie o arquivo .epw", type=["epw"])





if idf_file and epw_file:
    st.success("Arquivos carregados com sucesso!")

    # Salvar os arquivos enviados
    idf_path = os.path.join(UPLOAD_FOLDER, "input.idf")
    epw_path = os.path.join(UPLOAD_FOLDER, "weather.epw")

    with open(idf_path, "wb") as f:
        f.write(idf_file.getbuffer())

    with open(epw_path, "wb") as f:
        f.write(epw_file.getbuffer())

    # Botão para rodar a simulação
    if st.button("🔄 Rodar Simulação"):
        with st.spinner("Executando EnergyPlus..."):
            try:
                # Comando para rodar o EnergyPlus
                command = [
                    "EnergyPlus",
                    "-r",
                    "-d", OUTPUT_FOLDER,
                    "-w", epw_path,
                    "--expandobjects",
                    "--readvars",
                    idf_path
                ]

                # Executar o EnergyPlus
                result = subprocess.run(command, capture_output=True, text=True)
                

                if result.returncode != 0:
                    st.error(f"Erro ao rodar EnergyPlus: {result.stderr}")
        
            except Exception as e:
                st.error(f"Erro ao executar EnergyPlus: {str(e)}")

                # Exibir o arquivo de saída para download
            output_csv = os.path.join(OUTPUT_FOLDER, "eplusout.csv")
            if os.path.exists(output_csv):
                output_excel = csv_excel(output_csv)
                ajustar_largura_colunas_excel(output_excel)
                with open(output_excel, "rb") as f:
                    st.download_button(
                    "📥 Baixar Resultados (Excel)",
                    data=f,
                    file_name="resultados.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("Arquivo de resultados não encontrado.")