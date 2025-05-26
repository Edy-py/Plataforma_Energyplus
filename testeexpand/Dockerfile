FROM nrel/energyplus:latest

# Instalar Python e pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY requirements.txt .



# Instalar dependências
RUN pip3 install --no-cache-dir -r requirements.txt
# Expor a porta do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "expandapp.py", "--server.address=0.0.0.0"]


# FROM nrel/energyplus:latest

# # Instalar Python, pip e dependências necessárias
# RUN apt-get update && \
#     apt-get install -y python3 python3-pip && \
#     apt-get clean

# # Definir diretório de trabalho
# WORKDIR /app

# # Copiar arquivos necessários
# COPY requirements.txt .
# COPY expandapp.py .
# COPY volume/upload .

# # Instalar dependências (incluindo Streamlit)
# RUN pip3 install --no-cache-dir -r requirements.txt

# # Expor a porta do Streamlit
# EXPOSE 8501

# # Comando para rodar o Streamlit (com --server.address=0.0.0.0 para acesso externo)
# CMD ["streamlit", "run", "expandapp.py", "--server.address=0.0.0.0", "--server.port=8501"]