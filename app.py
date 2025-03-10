import streamlit as st
import pandas as pd
import subprocess
import os

# Configuração da Página
st.set_page_config(page_title="EnergyPlus Runner", layout="centered")

st.title("🏠 EnergyPlus Simulation")

# Upload dos arquivos
idf_file = st.file_uploader("Envie o arquivo .idf", type=["idf"])
epw_file = st.file_uploader("Envie o arquivo .epw", type=["epw"])

# Criar diretório de saída
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Se ambos os arquivos forem carregados
if idf_file and epw_file:
    # Salvar os arquivos localmente
    idf_path = os.path.join(output_dir, "input.idf")
    epw_path = os.path.join(output_dir, "weather.epw")

    with open(idf_path, "wb") as f:
        f.write(idf_file.getbuffer())

    with open(epw_path, "wb") as f:
        f.write(epw_file.getbuffer())

    st.success("Arquivos carregados com sucesso!")

    # Botão para rodar o EnergyPlus
    if st.button("🔄 Rodar Simulação"):
        with st.spinner("Executando EnergyPlus..."):
            # Comando para rodar o EnergyPlus
            result = subprocess.run(
                ["energyplus", "-r", "-d", output_dir, "-w", epw_path, "-r", idf_path],
                capture_output=True, text=True
            )

            if result.returncode == 0:
                st.success("Simulação concluída!")
            else:
                st.error("Erro ao executar EnergyPlus.")
                st.text(result.stderr)

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
