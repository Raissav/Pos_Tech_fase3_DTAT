# Guia didático de execução e entrega
## Tech Challenge — Fase 3 | Engenharia de Dados e Analytics na AWS

Preparado em 29 de outubro de 2026. Contexto: instituição financeira que pretende expandir Dados, Analytics e IA.

## 1. Antes de começar: o que já está pronto

O pacote contém apresentação executiva com 25 slides, gráficos e roteiro de fala; diagrama editável no formato Draw.io; dados originais; código do pipeline Spark; notebook de análise; SQL; resultados e auditorias locais.

O aluno informou que já criou o bucket no S3 e usou Glue para converter os CSVs em Parquet. O script original foi preservado. Não houve acesso ao AWS Academy Lab nesta preparação. Portanto, o novo pipeline, a integração do catálogo e as consultas Athena ainda precisam ser executados no Lab. Não entregue o material como se essa execução já tivesse acontecido.

Validação efetivamente realizada: Spark 3.5.6 local comparado com Pandas. Foram conferidas todas as 290 linhas de distribuições, 45 indicadores e 159 recortes salariais, além das contagens de qualidade. A escrita e a releitura Parquet de 14.002 registros também foram testadas. O arquivo resultados/validacao_spark.txt contém o relatório.

### Organização do pacote

- Apresentacao_Executiva.pptx e PDF: material executivo, com limitações e recomendações.
- Arquitetura_AWS.drawio: diagrama editável para abrir no Draw.io.
- Notebook_Analise.ipynb: análise reproduzível, gráficos e explicações.
- codigos/glue_job.py: job Spark de harmonização, qualidade, Silver, Gold e catalogação.
- codigos/config_pipeline.json: nomes exatos das origens, mapeamento e contrato de análise.
- codigos/consultas_athena.sql: consultas para análise, controle e exportação.
- codigos/analise_local.py: reprodução local independente do Spark.
- codigos/validar_spark_local.py: teste da transformação e da escrita Parquet em Spark local.
- codigos/reconciliar_athena.py: comparação automática dos exports reais com os resultados locais.
- codigos/gerar_entregaveis.py: gráficos e PowerPoint a partir dos resultados.
- dados_originais/: três CSVs sem alteração.
- resultados/: tabelas, anomalias, dicionário e controles de qualidade.
- graficos/: 17 gráficos PNG para reutilização.
- evidencias_aws/: local para reunir provas reais da execução; inicialmente sem screenshots.

## 2. Fontes e nomes das edições

A consulta pública ao catálogo de datasets de Data Hackers no Kaggle, em 29/10/2026, identificou as edições 2023–2024, 2024–2025 e 2025–2026 como as três mais recentes dentre as listadas dessa série. O registro consultado está em resultados/proveniencia_kaggle.json. Os nomes dos CSVs fornecidos usam 2023 e 2024; por isso o código usa os rótulos técnicos 2023, 2024 e 2025-2026. Não são cinco pesquisas diferentes.

- 2023: State_of_data_BR_2023_Kaggle - df_survey_2023.csv.
- 2024: Final Dataset - State of Data 2024 - Kaggle - df_survey_2024.csv.
- 2025–2026: Final Dataset - State of Data 2025-2026 - Kaggle.csv.

Não renomeie esses arquivos sem atualizar fontes.json e config_pipeline.json. Os hashes SHA-256 calculados a partir dos originais estão em resultados/sha256_fontes.json.

## 3. Entenda a arquitetura antes de clicar

Bronze é a camada de preservação dos CSVs originais. Neste projeto, o prefixo existente data-input/ cumpre esse papel lógico; não é obrigatório mover os arquivos para uma pasta chamada bronze.

O Glue Job lê as três edições com Spark, remove somente duplicatas exatas, verifica IDs, padroniza campos e trata anomalias com flags. A Silver guarda os registros harmonizados em Parquet Snappy, particionados por edicao_pesquisa. A Gold reúne tabelas agregadas para consulta. O próprio job cria/atualiza as tabelas no Glue Data Catalog e registra as partições da Silver. O Athena consulta essas tabelas. Os gráficos e o material executivo são gerados localmente, a partir de resultados reproduzíveis.

CloudWatch recebe os logs da execução. IAM controla permissões. Nenhum dashboard ou QuickSight é necessário. Não é necessário crawler no desenho proposto, porque o job cataloga diretamente; se o grupo preferir crawler, deverá documentar e validar essa mudança.

### Caminhos sugeridos no bucket existente

```text
s3://SEU_BUCKET/data-input/                       # Bronze: originais
s3://SEU_BUCKET/scripts/glue_job.py                # código
s3://SEU_BUCKET/scripts/config_pipeline.json       # contrato
s3://SEU_BUCKET/techchallenge/execucao=entrega_v1/silver/profissionais/
s3://SEU_BUCKET/techchallenge/execucao=entrega_v1/gold/distribuicoes/
s3://SEU_BUCKET/techchallenge/execucao=entrega_v1/gold/indicadores/
s3://SEU_BUCKET/techchallenge/execucao=entrega_v1/gold/salarios_segmentos/
s3://SEU_BUCKET/techchallenge/execucao=entrega_v1/gold/qualidade/
s3://SEU_BUCKET/athena-results/                    # resultados das consultas
```

O script original usava o bucket lab-223232422954. Confirme no console se ele continua disponível na conta e na região do Lab. Substitua SEU_BUCKET nos exemplos; não digite os sinais de menor/maior ou aspas como parte do valor.

## 4. Passo a passo no AWS Academy Lab

### Passo 1 — Ativar a sessão e confirmar a região

1. Entre no curso AWS Academy e abra o Learner Lab disponibilizado pela instituição.
2. Inicie a sessão e aguarde a liberação do console AWS.
3. Anote a região selecionada. Use a mesma região no S3, Glue e Athena.
4. Confirme o orçamento/saldo do laboratório. Os serviços podem consumir os créditos do Lab.
5. Não crie conta paga, chaves permanentes ou novas roles sem necessidade. Use as permissões disponíveis no laboratório.

Os nomes de telas e os recursos permitidos podem variar conforme o Lab. Se uma opção não estiver disponível, registre a restrição e consulte o docente; não declare ter utilizado um recurso bloqueado.

### Passo 2 — Conferir a Bronze no S3

1. Abra Amazon S3 e selecione o bucket já criado.
2. Entre no prefixo data-input/.
3. Verifique se os três CSVs aparecem, com os nomes exatamente iguais aos do pacote.
4. Se algum não estiver presente, faça upload do original correspondente.
5. Preserve os arquivos data-output/ da sua conversão anterior. O novo pipeline usa outra saída e não precisa apagá-los.
6. Crie o prefixo scripts/ e envie codigos/glue_job.py e codigos/config_pipeline.json.
7. Copie a URI S3 do JSON; ela será usada como CONFIG_S3_PATH.
8. Salve uma captura mostrando os três arquivos de entrada. Mascarar dados de conta na versão pública.

Não torne o bucket público. A entrega pode ser feita por arquivos baixados e screenshots, sem publicar dados e recursos do Lab.

### Passo 3 — Criar o Glue Job

1. Abra AWS Glue e a área de ETL jobs.
2. Escolha criar um job pelo editor de scripts Spark/Python, não Python Shell.
3. Nome sugerido: tc-fase3-state-of-data.
4. Use a role disponibilizada no Lab, frequentemente chamada LabRole, se ela estiver disponível e autorizada para Glue. Não tente criar roles adicionais se o laboratório bloquear essa ação.
5. Selecione Glue 5.1 quando disponível. Ele utiliza Spark 3.5.6, a mesma versão Spark do teste local. Glue 5.0 utiliza Spark 3.5.4 e pode ser uma alternativa, mas exige nova validação no Lab. Se apenas Glue 4.0 estiver disponível, não assuma compatibilidade sem testar.
6. Cole o conteúdo do script aprimorado ou selecione sua localização S3. Confirme que o código salvo é o novo, não o script original.
7. Para este volume, comece com 2 workers G.1X, se permitidos pelo Lab. Essa é uma configuração inicial proposta, não uma medida de performance ou custo.
8. Defina concorrência máxima 1 e retries 0 durante a validação. Defina timeout de 20 minutos como limite inicial e monitore a execução. Ajuste se necessário, sem deixar sessões ociosas.
9. Desabilite job bookmarks: este é um snapshot completo das três edições, não um pipeline incremental.
10. Evite configurar VPC/conexões adicionais sem necessidade do laboratório.

### Passo 4 — Preencher os parâmetros

Em Job details / Advanced properties / Job parameters, adicione:

```text
--CONFIG_S3_PATH = s3://SEU_BUCKET/scripts/config_pipeline.json
--INPUT_PREFIX   = s3://SEU_BUCKET/data-input
--OUTPUT_PREFIX  = s3://SEU_BUCKET/techchallenge
--RUN_ID         = entrega_v1
--DATABASE       = techchallenge_fase3
```

JOB_NAME é fornecido pelo Glue; não é necessário criar manualmente esse parâmetro. O INPUT_PREFIX deve apontar para a pasta que contém diretamente os três CSVs. Não use o caminho de um CSV específico como prefixo.

A saída será techchallenge/execucao=entrega_v1/. Rodar novamente com o mesmo RUN_ID sobrescreve esse snapshot, em vez de acumular novos arquivos. Use entrega_v2 para preservar uma versão anterior. O catálogo passa a apontar para a versão mais recentemente registrada. Não execute duas versões ao mesmo tempo e não consulte as tabelas durante uma sobrescrita. A atualização do conjunto de tabelas não é uma transação atômica.

Nunca use o bucket inteiro como OUTPUT_PREFIX. Não use a entrada como saída e não use purge_s3_path na Bronze. O código contém proteções de separação de caminhos; isso não dispensa a conferência visual antes de rodar.

### Passo 5 — Executar e acompanhar

1. Salve o job e capture a configuração, incluindo versão e parâmetros.
2. Clique em Run.
3. Abra a aba Runs e acompanhe o estado.
4. Entre nos logs CloudWatch associados ao run.
5. Busque as mensagens QUALIDADE e o resumo SUCESSO: snapshot e catálogo atualizados.
6. Confirme que o estado final é Succeeded, não apenas Running ou Stopping.
7. Anote JobRunId, horário e região. Salve screenshots reais e o trecho dos logs.

O código aplica portas de qualidade próprias em Spark, não AWS Glue Data Quality/DQDL. Uma falha de ID ou domínio binário gera exceção e impede a conclusão normal. Isso é intencional: não queremos publicar silenciosamente dados estruturalmente inválidos.

### Passo 6 — Conferir Silver e Gold no S3

1. No S3, abra techchallenge/execucao=entrega_v1/.
2. Na Silver, procure as partições edicao_pesquisa=2023, edicao_pesquisa=2024 e edicao_pesquisa=2025-2026.
3. Verifique arquivos .parquet nas três partições.
4. Na Gold, verifique as quatro pastas: distribuicoes, indicadores, salarios_segmentos e qualidade.
5. Não edite nem renomeie manualmente os arquivos part-*.parquet. Arquivos _SUCCESS, quando presentes, são marcadores, não dados de pesquisa.
6. Salve a captura da estrutura final.

### Passo 7 — Conferir o Glue Data Catalog

1. No Glue, abra Databases e selecione techchallenge_fase3.
2. Confira as cinco tabelas: silver_profissionais, gold_distribuicoes, gold_indicadores, gold_salarios_segmentos e gold_qualidade.
3. Na Silver, confirme edicao_pesquisa como chave de partição e as três partições cadastradas.
4. Confira o Location de cada tabela. Ele deve apontar para o RUN_ID atual e para a pasta da tabela, nunca para uma mistura de todas as camadas.
5. Salve uma captura das tabelas e uma da localização/partições.

### Passo 8 — Configurar e consultar no Athena

1. Abra Athena e o Query editor.
2. Selecione o catálogo AwsDataCatalog e o banco techchallenge_fase3.
3. Confirme que o workgroup está disponível e usa engine v3 quando configurável.
4. Nas configurações do workgroup/editor, informe uma saída de resultados permitida, por exemplo s3://SEU_BUCKET/athena-results/.
5. Abra codigos/consultas_athena.sql no seu computador.
6. Copie e execute UMA consulta por vez. Não cole todo o arquivo como uma única consulta.
7. Comece pelas consultas 01, 02 e 12: contagens, qualidade e integridade de chaves.
8. Depois execute as consultas analíticas de gênero, trabalho, salários, tecnologias e IA.
9. Salve screenshots que mostrem o SQL e os resultados, além dos CSVs exportados.

Não é necessário executar MSCK REPAIR TABLE, porque o job registra as três partições. Caso não apareçam, investigue a falha de catalogação antes de tentar reparar uma tabela apontando para caminho incorreto.

### Passo 9 — Usar os resultados esperados como teste

| Edição | Linhas originais | Duplicatas exatas | Linhas Silver | Residentes Brasil |
| --- | --- | --- | --- | --- |
| 2023 | 5.293 | 0 | 5.293 | 5.172 |
| 2024 | 5.217 | 2 | 5.215 | 5.076 |
| 2025–2026 | 3.495 | 1 | 3.494 | 3.372 |
| Total | 14.005 | 3 | 14.002 | 13.620 |

A consulta de chaves deve retornar zero duplicatas e zero nulos. A tabela de qualidade deve indicar 1/0/1 salários anômalos e 26/13/5 conflitos de IA, respectivamente.

Na Gold, os totais locais são: 290 linhas em distribuicoes, 45 em indicadores e 159 em salarios_segmentos. Esses números são linhas agregadas, não respondentes.

Se houver divergência, investigue o arquivo enviado, nomes, leitura de aspas, versão do código e configuração. Não altere os dados ou a contagem esperada apenas para fazer o teste passar. Se os CSVs forem substituídos por uma nova versão, refaça a análise e atualize a apresentação.

### Passo 10 — Reconciliação automática dos exports

Execute os três SELECT * ao final do SQL. Baixe cada resultado e renomeie SOMENTE a cópia baixada conforme a tabela:

- gold_distribuicoes → evidencias_aws/distribuicoes.csv.
- gold_indicadores → evidencias_aws/indicadores.csv.
- gold_salarios_segmentos → evidencias_aws/salarios_segmentos.csv.

No computador, dentro da pasta principal da entrega, execute:

```bash
python codigos/reconciliar_athena.py --pasta evidencias_aws
```

A ferramenta compara categorias, contagens, denominadores e percentuais, tolerando apenas diferenças numéricas de ponto flutuante muito pequenas. Com sucesso, grava evidencias_aws/reconciliacao_aws.txt. Ela não cria evidências de AWS: depende dos exports reais baixados pelo aluno.

## 5. Abrir e finalizar o diagrama no Draw.io

1. Acesse o Draw.io/diagrams.net ou abra o aplicativo desktop.
2. Escolha armazenamento local/dispositivo, conforme a opção disponível.
3. Use Abrir de / Dispositivo e selecione Arquitetura_AWS.drawio.
4. Confira os blocos Bronze, Glue/Spark, Silver, Gold, catálogo, Athena, gráficos e apresentação.
5. Ajuste os nomes para refletir o que foi realmente executado. Não adicione serviços não utilizados.
6. Após rodar no Lab, atualize a anotação de status e registre a identificação da versão executada.
7. Salve o arquivo editável pelo próprio Draw.io. Exporte PNG ou PDF legível e inclua a versão final na apresentação, se houver mudança.
8. Salve uma captura do diagrama aberto como evidência do uso da ferramenta.

O pacote contém um documento editável compatível com Draw.io, gerado programaticamente. Abrir, revisar e salvar na ferramenta é uma etapa explícita do grupo; não afirmamos que o aplicativo foi operado nesta preparação.

## 6. Como reproduzir a análise no computador

Abra um terminal na pasta principal do pacote. Recomenda-se Python 3.11 e Java 17 para o teste Spark, alinhados ao Glue 5.1. O teste realizado aqui usou Spark 3.5.6; versões locais de Python/Java podem variar e exigem validação própria.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r codigos/requirements.txt
python codigos/analise_local.py --entrada dados_originais --saida resultados
python codigos/validar_spark_local.py dados_originais resultados
python codigos/gerar_entregaveis.py
```

A análise local e os gráficos não exigem credenciais AWS. O teste Spark exige Java. Caso o sistema tenha restrição de permissão para escrita Spark, o validador usa uma pasta temporária local. No Windows, podem ser necessárias configurações adicionais de Java/Hadoop; nesse caso use o Lab para a execução obrigatória e mantenha o teste local como opcional de reprodução.

Abra Notebook_Analise.ipynb em Jupyter/VS Code. O notebook mostra os cálculos, a qualidade, os gráficos e o relatório do teste Spark; há uma célula opcional para repetir o teste, por ser mais demorado. Execute as células na ordem. As saídas fornecidas no notebook foram geradas dos arquivos anexados.

Para transformar PowerPoint e Word em PDF, abra no PowerPoint/Word/LibreOffice e use Exportar como PDF. Os PDFs fornecidos foram convertidos localmente. Ao alterar slides ou status, exporte novamente: não envie um PDF antigo com um PPTX atualizado.

## 7. Regras analíticas que você precisa saber explicar

### Unidade de análise e universo

Cada registro é uma resposta em uma edição. Uma pessoa pode ter participado de mais de uma edição; não somamos isso como pessoas únicas. A Silver preserva residentes e não residentes. As tabelas Gold analíticas filtram vive_no_brasil = 1. Nulos condicionais não são transformados em “não”. Recusas de gênero são preservadas como categoria do denominador.

### Deduplicação e identificação

Removemos somente linhas inteiramente idênticas dentro de cada CSV. Depois, validamos unicidade e preenchimento do identificador. IDs conflitantes fazem o job falhar, em vez de escolher uma resposta arbitrariamente. A Silver analítica usa hash SHA-256 de edição + identificador; não exporta o token original. Hash é pseudonimização, não garantia de anonimização. Os originais continuam preservados na Bronze com acesso restrito.

### Salário

Indicador: percentual em faixas de R$ 12.001/mês ou superiores = 100 × respostas em faixas válidas acima do corte / respostas com faixa válida no grupo. Não estimamos salário médio por ponto médio; não tratamos a última faixa aberta como valor exato. Valores são nominais, sem deflação e sem comparação causal.

Foram encontradas as faixas “de R$ 101/mês a R$ 2.000/mês” em 2023 e “de R$ 25.001/mês a R$ 3000/mês” em 2025–2026. São sinalizadas e excluídas dos cálculos salariais, sem presumir qual deveria ser a resposta. O registro permanece em todas as demais análises aplicáveis.

### Inteligência Artificial

ia_usa = 1 se a pessoa marca pelo menos uma das opções de uso gratuito, pago pelo próprio respondente, pago pela empresa ou Copilot. Se também marca “não uso”, o índice fica nulo por conflito. Se há respostas válidas e nenhuma opção de uso é marcada, ia_usa = 0. Se todas as opções estão ausentes, o índice permanece nulo.

A pergunta de uso pertence ao bloco técnico e não representa todos os participantes. A questão sobre resultados com LLMs pertence ao bloco de gestores. Seus percentuais têm denominadores diferentes. A unidade ainda é respondente, não empresa única. Não há medição objetiva de produtividade ou ROI; o impacto é percebido/declarado.

### Tecnologias e múltipla escolha

O percentual por opção é 100 × marcações 1 / respostas binárias válidas 0 ou 1 do item. Como a seleção é múltipla, os percentuais podem somar mais que 100%. Adoção declarada não é demanda por profissionais em vagas.

Os cabeçalhos de 2025–2026 indicam preferência para SQL/Python; os de 2023 indicam preferência no bloco cloud. Mantemos os valores na Silver para rastreabilidade, mas não os apresentamos como uma série homogênea de adoção. Essa limitação só poderia ser removida após verificar os questionários originais e confirmar a equivalência das perguntas.

### Diversidade, salários e confundimento

A participação feminina entre residentes passa de 24,5% para 22,0% nas amostras. Não é estimativa de saída de mulheres da carreira, nem de discriminação. A diferença salarial descritiva por gênero está disponível nos resultados, mas não foi ajustada por senioridade, cargo, setor ou jornada.

Recortes por cargo usam n mínimo 30 para o ranking exibido. Esse corte é uma regra de apresentação, não garantia de representatividade. O Norte tem apenas 36 respostas salariais válidas em 2025–2026. Não o interprete como comparável em precisão ao Sudeste. O SQL inclui um cruzamento cargo × senioridade para aprofundar o diagnóstico sem afirmar causalidade.

## 8. Como montar a entrega final

### Material executivo

Abra a apresentação, inclua integrantes, turma e data efetiva da entrega. Revise os gráficos e leia as notas do apresentador. A versão fornecida tem 25 slides; para uma fala de 15–20 minutos, selecione 12–15 slides centrais e mantenha os demais como apoio. Use o roteiro de apresentação como guia, não como texto para ler integralmente.

A narrativa sugerida é: problema de negócio → arquitetura e confiança nos dados → estrutura do mercado → contratação e remuneração → tecnologias e IA → recomendações de 90 dias. Evite começar com muitas telas de console: evidências técnicas ficam no apêndice/pacote.

Após executar no Lab, atualize os slides de status e conclusão com ID/data do job, versão Glue usada e comprovação de reconciliação. Não altere um indicador sem atualizar fonte e denominador. Se o diagrama mudou, substitua sua versão na apresentação. Gere novamente o PDF final.

### Organização para submissão

1. Apresentação executiva em PPTX e/ou PDF, conforme o canal da disciplina.
2. Diagrama dentro do material executivo e arquivo Draw.io editável adicional.
3. Notebook, scripts Spark/Python e SQL organizados em codigos/.
4. Resultados e dicionário que sustentam as análises.
5. Evidências reais de AWS e registro de reconciliação.
6. Guia/README com instruções de reprodução.

Não inclua senhas, access keys, secret keys, tokens de sessão, arquivos .env ou credenciais AWS na entrega. Não publique URLs assinadas ou dados de conta sem necessidade. Se o portal tiver limite de tamanho, envie os entregáveis centrais e a pasta de códigos conforme orientação do docente; preserve os originais em repositório autorizado ou anexo separado, sem mudar sua origem.

## 9. Checklist de conclusão

- [ ] Integrantes e turma incluídos na apresentação.
- [ ] Três edições confirmadas e arquivos originais preservados.
- [ ] AWS Academy Lab e região identificados.
- [ ] Glue/Spark concluído com Succeeded; JobRunId registrado.
- [ ] Silver e Gold em Parquet no S3.
- [ ] Cinco tabelas catalogadas e três partições Silver registradas.
- [ ] Contagens Athena batem com o esperado e chaves não se repetem.
- [ ] Exports Athena comparados com os resultados locais.
- [ ] Diagrama aberto, revisado e salvo no Draw.io.
- [ ] Screenshots reais adicionados, sem credenciais ou informações desnecessárias da conta.
- [ ] Status da apresentação atualizado; PPTX e PDF consistentes.
- [ ] Gráficos exibem universo, denominadores e limitações.
- [ ] Recomendações separadas de achados observados.
- [ ] Pacote final abre corretamente; prazo e forma de envio conferidos no portal.

## 10. Problemas frequentes e como resolver

### AccessDenied no Glue, S3 ou catálogo

Confira role do job, região e permissões disponíveis. O job precisa ler os três CSVs e o JSON, escrever no prefixo de saída, publicar logs e criar/atualizar banco, tabelas e partições Glue. No Lab, algumas ações podem ser bloqueadas. Use a role disponibilizada e peça orientação ao docente se necessário. Não abra o bucket publicamente para tentar resolver IAM. Se houver Lake Formation habilitado, permissões adicionais de catálogo/dados podem ser exigidas.

### NoSuchKey ou arquivo não encontrado

Confira nomes completos, espaços, maiúsculas e prefixo. INPUT_PREFIX contém a pasta, e config_pipeline.json contém os nomes dos arquivos. CONFIG_S3_PATH é a URI do JSON, não do script.

### Job falha com domínio inválido, ID conflitante ou coluna ausente

Não comente a validação para “fazer funcionar”. Confira se os arquivos são os mesmos do pacote; novas versões podem exigir revisão do contrato. Verifique aspas/multilinhas na leitura. Os CSVs são lidos com aspas duplas, escape por aspas duplas e multiLine habilitado; o teste local confirmou as contagens e os agregados com essa configuração.

### Athena não lista tabelas

Confira catálogo, banco e região. Veja se o job falhou na fase de catalogação. Os arquivos podem ter sido escritos antes de uma falha IAM, sem que o catálogo tenha sido atualizado. Corrija a permissão e reexecute o snapshot; não declare sucesso apenas pela presença dos Parquets.

### HIVE_BAD_DATA, schema incompatível ou partições ausentes

Confira o Location. Não consulte conjuntamente os Parquets antigos de esquemas diferentes em data-output/. Use a Silver harmonizada e as tabelas do novo job. Verifique se a tabela aponta para o RUN_ID atual e se as três partições foram registradas.

### Duplicidade após reexecução

A conversão original não define uma política explícita de reprocessamento. O novo job usa sobrescrita de snapshot dedicado. Não aponte uma tabela para múltiplos RUN_IDs, nem combine data-output/ com a Silver harmonizada.

### Encerramento do laboratório

Baixe códigos, screenshots e exports antes de encerrar. Siga a política do laboratório para retenção e limpeza. Cancele jobs desnecessários e interrompa sessões interativas não utilizadas. Não apague dados ou recursos de outros projetos.

## 11. Referências técnicas e de dados

Fontes primárias consultadas para configuração e proveniência; telas e permissões devem ser confirmadas no Lab.

- Enunciado fornecido: [DTAT] — Tech Challenge — Fase 3, páginas 2–5.
- Data Hackers / State of Data Brasil: datasets 2023–2024, 2024–2025 e 2025–2026, identificados no catálogo público Kaggle. Referências exatas e datas de atualização constam no JSON de proveniência.
- AWS Glue: Release notes / versions — https://docs.aws.amazon.com/glue/latest/dg/release-notes.html
- AWS Glue: Adding jobs — https://docs.aws.amazon.com/glue/latest/dg/add-job.html
- AWS Athena: Querying — https://docs.aws.amazon.com/athena/latest/ug/querying.html
- Transformações e resultados deste pacote: cálculos reproduzidos a partir dos três CSVs anexados, com contratos e testes de paridade incluídos.

A consulta ao catálogo identifica a série; não substitui a leitura dos questionários originais. As limitações semânticas encontradas foram mantidas explicitamente na análise.
