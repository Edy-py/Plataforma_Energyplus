## Plataforma EnergyPlus via Streamlit

Este repositório contém o código-fonte de uma plataforma web interativa para simulações do EnergyPlus, desenvolvida utilizando Streamlit. A plataforma permite aos usuários carregar arquivos de modelo EnergyPlus (IDF) e arquivos climáticos (EPW), executar simulações e visualizar os resultados de conforto térmico de forma amigável.

### Sobre o Desenvolvedor

Este projeto está sendo desenvolvido por Edilson Alves da Silva, estudante do 3º período de Ciência da Computação na UFCAT, como parte de uma Iniciação Científica sob a orientação do professor Wanderley. Este é o repositório de desenvolvimento pessoal, e um repositório final será criado ao término da Iniciação Científica.

### Objetivo

O principal objetivo desta plataforma é simplificar o processo de execução e análise de simulações do EnergyPlus, tornando-o mais acessível para pesquisadores e estudantes na área de eficiência energética e conforto térmico.

### Funcionalidades

* **Upload de Arquivos:** Permite o upload de arquivos `.epw` (dados climáticos) e `.idf` (modelo de construção do EnergyPlus) diretamente pela interface web.
* **Seleção de Zona:** Oferece a opção de selecionar diferentes zonas dentro do modelo para análise de conforto térmico.
* **Execução de Simulação:** Integra o motor de simulação EnergyPlus, executando-o em segundo plano e processando os resultados.
* **Análise de Conforto Térmico:** Calcula e exibe métricas de conforto térmico para as zonas e períodos selecionados.
* **Visualização de Dados:** Apresenta os resultados em tabelas e gráficos interativos.
* **Download de Resultados:** Permite o download dos dados de conforto térmico em formato Excel.

### Tecnologias Utilizadas

* **Streamlit:** Framework Python para criação de aplicativos web interativos.
* **EnergyPlus:** Motor de simulação de energia em edifícios.
* **Pandas:** Biblioteca para manipulação e análise de dados.
* **Openpyxl:** Biblioteca para leitura e escrita de arquivos Excel.
* **Docker:** Para conteinerização da aplicação.

### Como Usar

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o Aplicativo Streamlit:**
    ```bash
    streamlit run app.py
    ```

    Isso abrirá o aplicativo no seu navegador padrão.

### Executando com Docker

A plataforma pode ser executada via Docker. Um contêiner Docker está disponível publicamente.

1.  **Construir a Imagem Docker:**
    ```bash
    docker-compose build
    ```

2.  **Executar o Contêiner Docker:**
    ```bash
    docker-compose up
    ```

A aplicação estará acessível em `http://localhost:8501`.

### Plataforma Online

A plataforma está atualmente em execução em um servidor e pode ser acessada através dos seguintes links:

* **Servidor Docker:** [https://dockerstreamlit-production.up.railway.app](https://dockerstreamlit-production.up.railway.app)
* **Plataforma EnergyPlus:** [https://dockerstreamlit-production.up.railway.app/](https://dockerstreamlit-production.up.railway.app/)

### Estrutura do Repositório

* `app.py`: O arquivo principal do aplicativo Streamlit, responsável pela interface do usuário e orquestração das simulações.
* `functions.py`: Contém funções auxiliares para processamento de dados, manipulação de arquivos e cálculos de conforto térmico.
* `requirements.txt`: Lista as dependências Python necessárias para o projeto.
* `docker-compose.yml`: Define a configuração do serviço Docker para a aplicação.
* `.gitignore`: Especifica os arquivos e diretórios a serem ignorados pelo Git.
* `Materiais teste.xlsx - Planilha1.csv`: Um exemplo de arquivo CSV contendo dados de materiais de construção.

### Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.
