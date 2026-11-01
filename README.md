# 📊 Engenharia e Arquitetura de Dados: Pesquisa State of Data Brazil

[![AWS Glue](https://img.shields.io/badge/AWS-Glue%205.1-orange?logo=amazonaws)](https://aws.amazon.com/glue/)
[![PySpark](https://img.shields.io/badge/Engine-PySpark%203.5-firebrick?logo=apachespark)](https://spark.apache.org/)
[![Amazon S3](https://img.shields.io/badge/Storage-Amazon%20S3-green?logo=amazons3)](https://aws.amazon.com/s3/)
[![Amazon Athena](https://img.shields.io/badge/Analytics-Amazon%20Athena-blue?logo=amazonaws)](https://aws.amazon.com/athena/)

Este repositório contém a solução completa do **Tech Challenge - Fase 3** da pós-graduação em Data Engineering / Analytics Architecture. 

O objetivo do projeto é estruturar um pipeline de dados distribuído em nuvem AWS utilizando a **Arquitetura Medallion** (Camadas Bronze e Silver) para integrar, limpar e padronizar os dados das edições de **2023, 2024 e 2025-2026** da pesquisa **State of Data Brazil** (promovida pelo Data Hackers e Bain & Company).

---

## 📺 Apresentação Executiva

Conforme os requisitos do desafio, gravamos um vídeo de defesa técnica direcionado ao corpo docente e lideranças técnicas. O vídeo aborda a arquitetura na AWS, os desafios de padronização multi-safra, os insights extraídos e as ressalvas analíticas do estudo.

▶️ [**Assistir à Apresentação Executiva no YouTube**](https://youtu.be/SEU_LINK_AQUI)

---

## 👥 Autores do Projeto

O trabalho foi idealizado, projetado e executado de forma colaborativa pelos integrantes:
- **David da Silva Batista**
- **Jailson da Rosa Barduino**
- **Leonardo José da Silva**
- **Raíssa Vaz Viriato**
- **Yara Maria Santos Morais**

---

## 🏛️ Arquitetura de Dados na AWS

O pipeline foi construído seguindo os princípios de computação distribuída em nuvem e governança de dados:
```text
[ Dados Brutos (.csv) ] 
       │
       ▼
 ┌───────────┐      ┌─────────────────────────┐      ┌───────────┐      ┌───────────────┐
 │ Amazon S3 │ ───► │   AWS Glue (PySpark)    │ ───► │ Amazon S3 │ ───► │ AWS Glue Data │ ───► [ Amazon Athena ]
 │ (Bronze)  │      │ Processing & Encryption │      │ (Silver)  │      │    Catalog    │      │  (SQL Queries) │
 └───────────┘      └─────────────────────────┘      └───────────┘      └───────────────┘
```
## 📁 Estrutura de Pastas do Repositório

A estrutura deste repositório segue rigorosas boas práticas de Governança de Dados e Engenharia de Software:

```text
Pos_Tech_DTAT/
├── 📁 codigos/
│   ├── glue_job.py                    # Script PySpark executado no AWS Glue
│   └── config_pipeline.json           # Contrato de dados e configurações do pipeline
├── 📁 dados_originais/                # Datasets originais das pesquisas State of Data (2023-2026)
├── 📁 evidencias_aws/                 # Comprovantes de execução na nuvem (S3, Glue e Athena)
├── 📁 graficos/                       # Visualizações e gráficos gerados durante a análise
├── 📁 resultados/                     # Tabelas e recortes agregados resultantes do processamento
├── Apresentacao_Executiva.pdf         # Slides executivos da defesa técnica
├── Arquitetura_AWS.drawio             # Diagrama de arquitetura editável
├── Notebook_Analise.ipynb             # Notebook Jupyter com análise exploratória e reconciliação
├── Roteiro_De_Apresentacao.md         # Roteiro utilizado no vídeo executivo
└── README.md                          # Visão geral e guia do repositório
