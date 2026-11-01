📊 Engenharia de Dados e Análise Estratégica: State of Data Brazil

Este repositório contém a solução completa do Tech Challenge da pós-graduação. O projeto consiste em um pipeline de Engenharia de Dados de ponta a ponta construído na plataforma AWS, responsável por extrair, transformar e consolidar as edições da pesquisa State of Data Brazil (2023, 2024 e 2025-2026).

A solução aplica o padrão de Arquitetura Medallion, realizando o processamento distribuído via PySpark (AWS Glue), catalogação automatizada e consultas analíticas otimizadas através do Amazon Athena.

📺 Apresentação Executiva

Conforme os requisitos de comunicação executiva estabelecidos para o desafio, gravamos um vídeo de defesa técnica direcionado ao corpo diretivo e stakeholders. O vídeo aborda a arquitetura de dados na AWS, o tratamento das safras, os principais insights extraídos e as ressalvas analíticas do mercado de dados.

▶️ Assistir à Apresentação Executiva no YouTube

👥 Autores do Projeto

O trabalho foi idealizado, projetado e executado de forma colaborativa pelos integrantes:

David da Silva Batista

Jailson da Rosa Barduino

Leonardo José da Silva

Raíssa Vaz Viriato

Yara Maria Santos Morais

📁 Estrutura de Pastas do Repositório

A estrutura deste repositório segue rigorosas boas práticas de Governança de Dados e Engenharia de Software:

entrega/
 ├── 📁 codigos/                     # Scripts de ETL em PySpark (glue_job.py) e configurações (config_pipeline.json)
 ├── 📁 dados_originais/             # Datasets brutos (State of Data 2023, 2024 e 2025-2026)
 ├── 📁 evidencias_aws/              # Evidências de execução na AWS (S3, AWS Glue Job e Amazon Athena)
 ├── 📁 graficos/                    # Gráficos e visualizações geradas na análise exploratória
 ├── 📁 resultados/                  # Métricas consolidadas e saídas analíticas
 ├── Apresentacao_Executiva.pdf      # Deck de slides executivos direcionado a stakeholders
 ├── Arquitetura_AWS.drawio          # Diagrama arquitetural editável do pipeline de dados
 ├── Guia_Didatico.md                # Documentação técnica e conceitual aprofundada do projeto
 ├── Notebook_Analise.ipynb          # Jupyter Notebook com EDA, limpeza e reconciliação dos dados
 ├── README.md                       # Documentação principal e guia de navegação
 └── Roteiro_De_Apresentacao.md      # Roteiro de defesa técnica e comunicação executiva


🏗️ Arquitetura da Solução na AWS

A infraestrutura foi provisionada no ambiente AWS Academy Learner Lab utilizando uma abordagem escalável e desacoplada:

[ Dados Brutos (CSV) ] 
          │
          ▼
  [ Amazon S3 (Bronze) ] 
          │
          ▼
  [ AWS Glue (PySpark ETL) ] ───► [ AWS Glue Data Catalog ]
          │                                 │
          ▼                                 ▼
  [ Amazon S3 (Silver - Parquet) ] ───► [ Amazon Athena (SQL Queries) ]


Amazon S3 (data-input/ - Camada Bronze): Armazenamento seguro dos arquivos originais em formato CSV referente às três safras da pesquisa.

AWS Glue Job (PySpark): Processamento distribuído responsável por padronização de esquemas, tratamento de nulos, deduplicação e conversão para formato colunar de alta performance (Parquet).

AWS Glue Data Catalog: Registro centralizado do banco de dados (tech_challenge_db) e metadados das tabelas particionadas.

Amazon Athena: Camada de visualização e consulta ad-hoc em SQL para validação de métricas salariais, perfil demográfico e tendências de mercado.

📸 Evidências de Execução

As comprovações da execução prática na AWS estão catalogadas no diretório evidencias_aws/:

S3 Bucket: Estruturação dos prefixos data-input/, scripts/ e silver/.

AWS Glue Job: Histórico de execução concluído com status verde Succeeded.

Amazon Athena: Validação volumétrica de paridade dos dados (14.002+ registros reconciliados).
