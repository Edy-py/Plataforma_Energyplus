from functions import *
import subprocess


# Configuração do título Streamlit
st.title("🏠 EnergyPlus Simulation via Streamlit")

# Diretórios de trabalho
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

# Garantir que os diretórios existem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Inicializa variáveis de estado
if "epw_file" not in st.session_state:
    st.session_state.epw_file = None
if "idf_file" not in st.session_state:
    st.session_state.idf_file = None

# Lista arquivos existentes
existing_files = os.listdir(UPLOAD_FOLDER)

# Escolha ou upload de arquivo EPW
epw_choice = st.selectbox("Escolha um arquivo pré-existente na plataforma:", ["Nenhum arquivo selecionado"] + existing_files)

if epw_choice != "Nenhum arquivo selecionado":
    st.session_state.epw_file = os.path.join(UPLOAD_FOLDER, epw_choice)
else:
    uploaded_epw = st.file_uploader("Envie o arquivo .epw", type=["epw"])
    if uploaded_epw is not None:
        epw_path = os.path.join(UPLOAD_FOLDER, uploaded_epw.name)
        with open(epw_path, "wb") as f:
            f.write(uploaded_epw.getbuffer())
        st.session_state.epw_file = epw_path

# Prepara o caminho do epw somente se tiver arquivo
if st.session_state.epw_file:
    epw_path = os.path.join(UPLOAD_FOLDER, "weather.epw")
    with open(st.session_state.epw_file, "rb") as src, open(epw_path, "wb") as dst:
        dst.write(src.read())

# Upload do arquivo IDF
idf_file = st.file_uploader("Envie o arquivo .idf", type=["idf"])
if idf_file is not None:
    idf_path = os.path.join(UPLOAD_FOLDER, idf_file.name)
    with open(idf_path, "wb") as f:
        f.write(idf_file.getbuffer())
    st.session_state.idf_file = idf_path

# SelectBox para temperatura
TempZonas = {
    'Zona 1': (27.68, 20.68),
    'Zona 2': (25.58, 18.58),
    'Zona 3': (27.18, 20.18),
    'Zona 4': (27.25, 20.25),
    'Zona 5': (26.34, 19.34),
    'Zona 6': (27.66, 20.66),
    'Zona 7': (29.81, 22.81),
    'Zona 8': (29.57, 22.57)
}

if "zona_selecionada" not in st.session_state:
    st.session_state.zona_selecionada = list(TempZonas.keys())[0]

zona_selecionada = st.selectbox(
    "Selecione a zona",
    list(TempZonas.keys()),
    index=list(TempZonas.keys()).index(st.session_state.zona_selecionada)
)
st.session_state.zona_selecionada = zona_selecionada
MAX_TEMP, MIN_TEMP = TempZonas[zona_selecionada]

ano = st.number_input("Selecione o ano", min_value=2025, value=2025, step=1)

# Verifica se os arquivos foram carregados
if st.session_state.idf_file and st.session_state.epw_file and zona_selecionada:
    st.success("Arquivos carregados com sucesso!")

    idf_path = os.path.join(UPLOAD_FOLDER, "input.idf")
    with open(st.session_state.idf_file, "rb") as src, open(idf_path, "wb") as dst:
        dst.write(src.read())

    if "simulacao_executada" not in st.session_state:
        st.session_state.simulacao_executada = False

    if st.button("🔄 Rodar Simulação"):
        with st.spinner("Executando EnergyPlus..."):
            try:
                command = ["EnergyPlus", "-r", "-d", OUTPUT_FOLDER, "-w", epw_path, "--expandobjects", "--readvars", idf_path]
                result = subprocess.run(command, capture_output=True, text=True)

                if result.returncode != 0:
                    st.error(f"Erro ao rodar EnergyPlus: {result.stderr}")
                    st.stop()

            except Exception as e:
                st.error(f"Erro ao executar EnergyPlus: {str(e)}")
                st.stop()

            st.session_state.simulacao_executada = True

            output_csv = os.path.join(OUTPUT_FOLDER, "eplusout.csv")
            if os.path.exists(output_csv):
                output_excel = csv_excel(output_csv, OUTPUT_FOLDER)
                ajustar_largura_colunas_excel(output_excel)
                df_excel = pd.read_excel(output_excel)

                st.session_state.dataframe_conforto = processar_arquivo_temperatura(df_excel, MIN_TEMP, MAX_TEMP, ano)

# Mostrar resultados
if st.session_state.get("simulacao_executada") and "dataframe_conforto" in st.session_state:
    os.remove(epw_path)
    os.remove(idf_path)

    dataframe_conforto = st.session_state.dataframe_conforto
    st.sidebar.header("🎛️ Filtros")

    if not dataframe_conforto.empty:
        opcoes_meses = ["Todos"] + sorted(dataframe_conforto['Mês'].dropna().unique().tolist())
        mes = st.sidebar.selectbox("Selecione o mês", opcoes_meses)

        opcoes_locais = ["Todos"] + sorted(dataframe_conforto['Local'].dropna().unique().tolist())
        local = st.sidebar.selectbox("Selecione o local", opcoes_locais)

        df_filtrado = dataframe_conforto.copy()
        if mes != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Mês'] == mes]
        if local != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Local'] == local]

        if mes == "Todos" and local == "Todos":
            st.write("### Resultados de Conforto Térmico (Todos os meses e locais)")
        elif mes != "Todos" and local != "Todos":
            st.write(f"### Resultados de Conforto Térmico para o mês de :blue[{mes}] e local :blue[{local}]")
        elif mes != "Todos":
            st.write(f"### Resultados de Conforto Térmico para o mês de :blue[{mes}]")
        else:
            st.write(f"### Resultados de Conforto Térmico para o local :blue[{local}]")

        st.dataframe(df_filtrado)

        st.subheader("📊 Gráfico de Área - Indicadores de Conforto")
        df_grafico = df_filtrado[['Mês', 'Conforto (Dia)', 'Conforto (Noite)', 'Total Conforto', 'Sem Conforto']].copy()
        df_grafico_grouped = df_grafico.groupby('Mês').sum(numeric_only=True).sort_index()

        st.bar_chart(df_grafico_grouped)

        caminho_excel = os.path.join(OUTPUT_FOLDER, "Tabela_conforto.xlsx")
        df_filtrado.to_excel(caminho_excel, index=False)
        ajustar_largura_colunas_excel(caminho_excel)

        with open(caminho_excel, "rb") as f:
            st.sidebar.download_button(
                "📅 Baixar Tabela de Conforto Completa (Excel)",
                data=f,
                file_name="Tabela_conforto.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("⚠️ Nenhum dado de conforto térmico encontrado para exibir.")
