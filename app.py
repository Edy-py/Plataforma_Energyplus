from functions import *
import subprocess


# Configuração do título Streamlit
st.title("🏠 EnergyPlus Simulation via Streamlit")
# Diretório de trabalho
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
# Verifica se o diretório de saída existe, caso contrário, cria
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


existing_files = os.listdir(UPLOAD_FOLDER)
# Disponibiliza ao usuário a opção de escolher um arquivo já existente ou fazer upload de um novo
epw_file = st.selectbox("Escolha um arquivo pré-existente na plataforma:", ["Nenhum arquivo selecionado"] + existing_files)

if epw_file != "Nenhum arquivo selecionado":
    file_path = os.path.join(UPLOAD_FOLDER, epw_file)
    epw_path = os.path.join(UPLOAD_FOLDER, "weather.epw")
else:
    st.write("Você não selecionou nenhum arquivo epw (selecione algum ou faça upload do mesmo): ")
    epw_file = st.file_uploader("Envie o arquivo .epw", type=["epw"])
    if epw_file:
        epw_path = os.path.join(UPLOAD_FOLDER, "weather.epw")
        with open(epw_path, "wb") as f:
            f.write(epw_file.getbuffer())

# Caixa para o upload do arquivo IDF
idf_file = st.file_uploader("Envie o arquivo .idf", type=["idf"])

# Verifica se os arquivos foram carregados
if idf_file and epw_file:
    st.success("Arquivos carregados com sucesso!")
    idf_path = os.path.join(UPLOAD_FOLDER, "input.idf")
    with open(idf_path, "wb") as f:
        f.write(idf_file.getbuffer()) # Carrega o arquivo na plataforma

    # Verifica se a simulação já foi executada se não, inicializa a variável de controle
    if "simulacao_executada" not in st.session_state:
        st.session_state.simulacao_executada = False

    # Botão para rodar a simulação do EnergyPlus
    if st.button("🔄 Rodar Simulação"):
        with st.spinner("Executando EnergyPlus..."):
            try:
                command = ["EnergyPlus", "-r", "-d", OUTPUT_FOLDER, "-w", epw_path, "--expandobjects", "--readvars", idf_path]
                result = subprocess.run(command, capture_output=True, text=True)
                if result.returncode != 0:
                    st.error(f"Erro ao rodar EnergyPlus: {result.stderr}")
                    st.stop() # Para evitar que o código continue em caso de erro
            except Exception as e:
                st.error(f"Erro ao executar EnergyPlus: {str(e)}")
                st.stop() # Para evitar que o código continue em caso de erro

            # indica que a simulação foi executada
            st.session_state.simulacao_executada = True

            output_csv = os.path.join(OUTPUT_FOLDER, "eplusout.csv") # o arquivo "eplusout.csv" é gerado pelo EnergyPlus, ele possui os resultados da simulação
            if os.path.exists(output_csv):
                output_excel = csv_excel(output_csv, OUTPUT_FOLDER)
                ajustar_largura_colunas_excel(output_excel)
                df_excel = pd.read_excel(output_excel)
                st.session_state.dataframe_conforto = analisar_conforto_termico(df_excel) # Análise de conforto térmico 

# Mostrar resultados apenas se simulação foi feita
if st.session_state.get("simulacao_executada") and "dataframe_conforto" in st.session_state:
    dataframe_conforto = st.session_state.dataframe_conforto
    st.sidebar.header("🎛️ Filtros")

    # Verifica se o dataframe de conforto térmico não está vazio
    if not dataframe_conforto.empty:
        # Filtros para mês
        opcoes_meses = ["Todos"] + sorted(dataframe_conforto['Mês'].dropna().unique().tolist()) # Cria uma lista de meses únicos encontrados no dataframe
        mes = st.sidebar.selectbox("Selecione o mês", opcoes_meses)

        #filtros para local
        opcoes_locais = ["Todos"] + sorted(dataframe_conforto['Local'].dropna().unique().tolist())
        local = st.sidebar.selectbox("Selecione o local", opcoes_locais)

        df_filtrado = dataframe_conforto.copy() # A variável df_filtrado é uma cópia do dataframe original para não alterar o original
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

        # Exibe o dataframe filtrado na plataforma, para que o usuário possa visualizar os resultados
        st.dataframe(df_filtrado)

        # Gráfico de área
        st.subheader("📊 Gráfico de Área - Indicadores de Conforto")
        df_grafico = df_filtrado[[
            'Mês', 'Conforto (Dia)', 'Conforto (Noite)', 'Total Conforto', 'Sem Conforto'
        ]].copy()

        # Agrupamento por mês para somar os valores
        df_grafico_grouped = df_grafico.groupby('Mês').sum(numeric_only=True) # O método groupby() agrupa os dados por mês e soma os valores
        df_grafico_grouped = df_grafico_grouped.sort_index() # O método sort_index() ordena os dados pelo índice (mês)

        st.bar_chart(df_grafico_grouped) # Gráfico de barras


        caminho_excel = os.path.join(OUTPUT_FOLDER, "Tabela_conforto.xlsx")
        df_filtrado.to_excel(caminho_excel, index=False)
        tabela_formatada = ajustar_largura_colunas_excel(caminho_excel)
        with open(caminho_excel, "rb") as f:
            st.sidebar.download_button(
                "📅 Baixar Tabela de Conforto Completa (Excel)",
                data=f,
                file_name="Tabela_conforto.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("⚠️ Nenhum dado de conforto térmico encontrado para exibir.")
