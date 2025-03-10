# Usar a imagem oficial do EnergyPlus
FROM nrel/energyplus:latest

# Evitar interação manual no apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Atualizar pacotes e instalar dependências
RUN apt-get update && apt-get install -y python3-pip wget libglib2.0-0 libsm6 libxrender1 libfontconfig1

# Instalar bibliotecas Python necessárias
RUN pip3 install streamlit pandas openpyxl

# Criar diretório de trabalho
WORKDIR /app

# Copiar código do Streamlit para o contêiner
COPY . .

# Expor a porta do Streamlit
EXPOSE 8501



# Comando para rodar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
