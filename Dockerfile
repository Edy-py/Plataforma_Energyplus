FROM nrel/energyplus:latest

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos do projeto para o container
COPY . /app

# Instalar dependências Python
RUN pip install --no-cache-dir flask

# Expor a porta do Flask
EXPOSE 5000

# Comando para rodar a API Flask
CMD ["python", "app.py"]
