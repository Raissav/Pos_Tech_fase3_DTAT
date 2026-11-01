-- Engine Athena v3. Selecionar o banco techchallenge_fase3 no editor.
-- O Glue Job já cria/atualiza as tabelas e registra as partições; não é necessário crawler.
-- Executar cada consulta separadamente. Exportar resultados e screenshots para evidencias_aws.

-- 01. Reconciliação: 2023=5293; 2024=5215; 2025-2026=3494; total=14002.
SELECT edicao_pesquisa, count(*) AS linhas_silver,
       count_if(vive_no_brasil=1) AS residentes_brasil,
       count(DISTINCT respondente_chave) AS chaves_distintas
FROM silver_profissionais GROUP BY 1 ORDER BY 1;

-- 02. Qualidade: duplicatas 0/2/1; salários anômalos 1/0/1; IA conflitante 26/13/5.
SELECT * FROM gold_qualidade ORDER BY edicao;

-- 03. Gênero. Denominador: residentes com resposta no campo, inclui 'Outro' e recusa.
SELECT edicao_pesquisa,categoria,n,denominador,round(percentual,2) AS percentual
FROM gold_distribuicoes WHERE dimensao='genero' ORDER BY 1,3 DESC;

-- 04. Modelo atual vs ideal. A soma de remoto + híbrido flexível ideal em 2025–2026 = 85,24%.
SELECT dimensao,categoria,n,denominador,round(percentual,2) AS percentual
FROM gold_distribuicoes WHERE edicao_pesquisa='2025-2026'
AND dimensao IN ('modelo_atual','modelo_ideal') ORDER BY dimensao,n DESC;

-- 05. Perfis valorizados: salário em faixa iniciada em R$ 12.001/mês ou superior.
-- Não é salário médio, prêmio causal nem demanda de vagas. Corte n>=30 para evitar ranks muito pequenos.
SELECT categoria,n_salario_alto,denominador,round(percentual,2) AS percentual
FROM gold_salarios_segmentos WHERE edicao_pesquisa='2025-2026'
AND dimensao='cargo' AND denominador>=30 ORDER BY percentual DESC;

-- 06. Recortes descritivos; diferenças não ajustadas por cargo/senioridade/região.
SELECT dimensao,categoria,n_salario_alto,denominador,round(percentual,2) AS percentual
FROM gold_salarios_segmentos WHERE edicao_pesquisa='2025-2026'
AND dimensao IN ('senioridade','regiao','modelo_atual','genero') ORDER BY 1,5 DESC;

-- 07. Tecnologias. SQL/Python em 2025–2026 têm cabeçalho de preferência: NÃO chamar de adoção.
-- Cloud em 2023 também tem cabeçalho de preferência: não unir em série de adoção.
SELECT edicao_pesquisa,indicador,n,denominador,round(percentual,2) AS percentual
FROM gold_indicadores WHERE
(edicao_pesquisa='2024' AND indicador IN ('sql','python')) OR
(edicao_pesquisa='2025-2026' AND indicador IN ('aws','azure','gcp','powerbi','tableau'))
ORDER BY 1,5 DESC;

-- 08. IA: exclui conflitos 'não uso' + uso positivo do cálculo de ia_usa; demais indicadores independentes.
SELECT edicao_pesquisa,indicador,n,denominador,round(percentual,2) AS percentual
FROM gold_indicadores WHERE indicador IN ('ia_usa','ia_paga_empresa','ia_centralizada','ia_descentralizada')
ORDER BY 2,1;

-- 09. Impacto percebido pelos respondentes do bloco de gestores, não contagem de empresas únicas.
SELECT categoria,n,denominador,round(percentual,2) AS percentual
FROM gold_distribuicoes WHERE edicao_pesquisa='2025-2026' AND dimensao='ia_resultado'
ORDER BY n DESC;

-- 10. Finanças/Bancos versus outros setores com salário válido. Não interpretar como efeito do setor.
SELECT CASE WHEN setor='Finanças ou Bancos' THEN 'Finanças ou Bancos' ELSE 'Outros setores' END AS segmento,
       count(*) AS n_validos, sum(salario_alto) AS n_salario_alto,
       round(100.0*sum(salario_alto)/count(*),2) AS pct_salario_alto
FROM silver_profissionais
WHERE edicao_pesquisa='2025-2026' AND vive_no_brasil=1 AND setor IS NOT NULL AND salario_alto IS NOT NULL
GROUP BY 1;

-- 11. Análise controlada descritiva: cruza cargo e senioridade em vez de atribuir causalidade.
SELECT cargo,senioridade,count(*) AS n,
       round(100.0*sum(salario_alto)/count(*),2) AS pct_salario_alto
FROM silver_profissionais WHERE edicao_pesquisa='2025-2026' AND vive_no_brasil=1
AND salario_alto IS NOT NULL AND cargo IS NOT NULL AND senioridade IS NOT NULL
GROUP BY 1,2 HAVING count(*)>=30 ORDER BY 1,2;

-- 12. Portas de qualidade que devem retornar zero.
SELECT count(*)-count(DISTINCT respondente_chave) AS chaves_repetidas,
       count_if(respondente_chave IS NULL) AS chaves_nulas FROM silver_profissionais;

-- 13. Exportar integralmente estes 3 resultados para a reconciliação automática.
-- Nomear os arquivos baixados em evidencias_aws conforme comentários.
SELECT * FROM gold_distribuicoes; -- distribuicoes.csv
SELECT * FROM gold_indicadores; -- indicadores.csv
SELECT * FROM gold_salarios_segmentos; -- salarios_segmentos.csv
