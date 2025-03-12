import streamlit as st
import os
import subprocess

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
                    idf_path
                ]

                # Executar o EnergyPlus
                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode != 0:
                    st.error(f"Erro ao rodar EnergyPlus: {result.stderr}")
                else:
                    st.success("Simulação concluída com sucesso!")

                    # Exibir o arquivo de saída para download
                    output_csv = os.path.join(OUTPUT_FOLDER, "eplusout.csv")
                    if os.path.exists(output_csv):
                        with open(output_csv, "rb") as f:
                            st.download_button(
                                label="📥 Baixar Resultados",
                                data=f,
                                file_name="resultados.csv",
                                mime="text/csv"
                            )
                    else:
                        st.error("Arquivo de resultados não encontrado.")
            except Exception as e:
                st.error(f"Erro ao executar EnergyPlus: {str(e)}")