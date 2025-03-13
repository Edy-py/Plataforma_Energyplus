FROM nrel/energyplus:latest

# Instalar Python e pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências
RUN pip3 install --no-cache-dir streamlit
RUN pip3 install --no-cache-dir openpyxl

# Expor a porta do Streamlit
EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]