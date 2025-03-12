import streamlit as st
import pandas as pd
import os
import requests
from eppy.modeleditor import IDF


# Configuração da Página
st.set_page_config(page_title="EnergyPlus Runner", layout="centered")

st.title("🏠 EnergyPlus Simulation")

# Criar diretório de saída
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)


def get_idd():
    # URL do arquivo .idd
    idd_url = "https://raw.githubusercontent.com/NREL/EnergyPlus/refs/heads/develop/idd/versions/V24-1-0-Energy%2B.idd"

    # Baixar o arquivo .idd
    idd_path = os.path.join(output_dir, "energyplus.idd")

    if not os.path.exists(idd_path):
        st.write("Baixando o arquivo .idd...")
        response = requests.get(idd_url)
        if response.status_code == 200:
            with open(idd_path, "wb") as f:
                f.write(response.content)
            st.success("Arquivo .idd baixado com sucesso!")
        else:
            st.error(f"Erro ao baixar o arquivo .idd. Status: {response.status_code}")
    return idd_path

# Upload dos arquivos
idd_path = get_idd()
idf_file = st.file_uploader("Envie o arquivo .idf", type=["idf"])
epw_file = st.file_uploader("Envie o arquivo .epw", type=["epw"])
print(idd_path)



# Se os arquivos IDF e EPW  forem carregados
if idf_file and epw_file:
    # Salvar os arquivos localmente
    idf_path = os.path.join(output_dir, "input.idf")
    epw_path = os.path.join(output_dir, "weather.epw")

    with open(idf_path, "wb") as f:
        f.write(idf_file.getbuffer())

    with open(epw_path, "wb") as f:
        f.write(epw_file.getbuffer())

    st.success("Arquivos carregados com sucesso!")

    # Botão para rodar a simulação
    if st.button("🔄 Rodar Simulação"):
        try:
            with st.spinner("Executando EnergyPlus..."):
                # Carregar o IDF com eppy
                IDF.setiddname(idd_path)  # Usando o caminho do arquivo .idd baixado

                # Carregar o arquivo IDF e EPW
                idf = IDF(idf_path,epw_path)
                
                
                # Executar a simulação
                if st.button("🔄 Rodar Simulação"):
                    try:
                        with st.spinner("Enviando arquivos para processamento..."):
                            files = {
                                "idf": open(idf_path, "rb"),
                                "epw": open(epw_path, "rb")
                            }
                            response = requests.post("https://seu-app-no-railway.up.railway.app/run-energyplus", files=files)

                            if response.status_code == 200:
                                with open("resultados.csv", "wb") as f:
                                    f.write(response.content)
                                
                                st.success("Simulação concluída com sucesso! Faça o download dos resultados abaixo:")
                                
                                # Permitir download
                                with open("resultados.csv", "rb") as f:
                                    st.download_button("📥 Baixar Resultados", f, file_name="resultados.csv")

                            else:
                                st.error(f"Erro ao processar a simulação: {response.json().get('error', 'Erro desconhecido')}")

                    except Exception as e:
                        st.error(f"Erro ao enviar os arquivos: {str(e)}")

                
                st.success("Simulação concluída com sucesso!")

        except Exception as e:
            st.error(f"Erro ao executar EnergyPlus: {str(e)}")

    # Verifica se o CSV foi gerado
    csv_file = os.path.join(output_dir, "eplusout.csv")
    xlsx_file = os.path.join(output_dir, "eplusout.xlsx")

    if os.path.exists(csv_file):
        # Converter CSV para XLSX
        df = pd.read_csv(csv_file)
        df.to_excel(xlsx_file, index=False)

        # Permitir download do XLSX
        with open(xlsx_file, "rb") as f:
            st.download_button(
                label="📥 Baixar XLSX",
                data=f,
                file_name="resultados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )