FROM nrel/energyplus:latest

# Instalar Python e pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto para o container
COPY . /app

# Instalar dependências Python (Flask)
RUN pip3 install --no-cache-dir flask

# Expor a porta do Flask
EXPOSE 5000

# Comando para rodar a API Flask
CMD ["python3", "server.py"]
