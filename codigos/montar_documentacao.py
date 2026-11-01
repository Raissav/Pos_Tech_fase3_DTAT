from pathlib import Path
import re,json
import nbformat as nbf
from nbclient import NotebookClient
from docx import Document
from docx.shared import Inches,Pt,RGBColor
BASE=Path(__file__).resolve().parent.parent
# Guia Word editável a partir do Markdown.
doc=Document();sec=doc.sections[0];sec.top_margin=Inches(.7);sec.bottom_margin=Inches(.65);sec.left_margin=Inches(.8);sec.right_margin=Inches(.8)
styles=doc.styles
styles['Normal'].font.name='Calibri';styles['Normal'].font.size=Pt(10.5);styles['Normal'].paragraph_format.space_after=Pt(6)
for h in ['Title','Heading 1','Heading 2','Heading 3']:
 styles[h].font.name='Calibri';styles[h].font.color.rgb=RGBColor.from_string('14283F')
styles['Heading 1'].font.size=Pt(19);styles['Heading 2'].font.size=Pt(15);styles['Heading 3'].font.size=Pt(12)
lines=(BASE/'Guia_Didatico.md').read_text().splitlines();code=False;tablelines=[]
def flush_table():
 if not tablelines:return
 data=[[c.strip() for c in l.strip().strip('|').split('|')] for l in tablelines if not re.match(r'^\|[\s|:-]+\|$',l)]
 table=doc.add_table(rows=len(data),cols=len(data[0]));table.style='Light Shading Accent 1'
 for r,row in enumerate(data):
  for c,v in enumerate(row):table.cell(r,c).text=v
 tablelines.clear()
for line in lines:
 if line.startswith('|'):tablelines.append(line);continue
 flush_table()
 if line.startswith('```'):code=not code;continue
 if not line.strip():continue
 if code:
  p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);r=p.add_run(line);r.font.name='Consolas';r.font.size=Pt(8);continue
 if line.startswith('# '):doc.add_heading(line[2:],0)
 elif line.startswith('### '):doc.add_heading(line[4:],2)
 elif line.startswith('## '):doc.add_heading(line[3:],1)
 elif line.startswith('- '):doc.add_paragraph(line[2:],style='List Bullet')
 elif re.match(r'^\d+\. ',line):doc.add_paragraph(re.sub(r'^\d+\. ','',line),style='List Number')
 else:doc.add_paragraph(line)
flush_table();sec.footer.paragraphs[0].text='Tech Challenge — Fase 3 | Guia de execução e entrega | Verificar execução AWS antes da submissão'
doc.save(BASE/'Guia_Didatico.docx')
# Notebook executável com resultados reais.
nb=nbf.v4.new_notebook();cells=[]
def md(t):cells.append(nbf.v4.new_markdown_cell(t))
def code(t):cells.append(nbf.v4.new_code_cell(t))
md('''# State of Data Brasil — Tech Challenge Fase 3
## Engenharia de Dados e Analytics para uma instituição financeira
**Universo analítico:** respostas de residentes no Brasil, por edição, após remoção de duplicatas exatas.
**Status:** análise e Spark validados localmente. Execução AWS e evidências dependem do AWS Academy Lab.

Este notebook não utiliza credenciais AWS e não simula execução no Glue. O pipeline cloud está em `codigos/glue_job.py`. Leia o guia didático antes de executá-lo no laboratório.''')
code('''from pathlib import Path
import sys, json, subprocess
import pandas as pd
from IPython.display import display, Image
BASE = Path.cwd()
if not (BASE / 'codigos').exists():
    raise RuntimeError('Abra o notebook a partir da pasta principal entrega/.')
sys.path.insert(0, str(BASE / 'codigos'))
from analise_local import run
silver = run(BASE / 'dados_originais', BASE / 'resultados')
brasil = silver[silver.vive_no_brasil.eq(1)].copy()
distribuicoes = pd.read_csv(BASE/'resultados/distribuicoes.csv', dtype={'edicao_pesquisa':str})
indicadores = pd.read_csv(BASE/'resultados/indicadores.csv', dtype={'edicao_pesquisa':str})
salarios = pd.read_csv(BASE/'resultados/salarios_segmentos.csv', dtype={'edicao_pesquisa':str})
print('Linhas Silver:', len(silver))
print('Respostas residentes no Brasil:', len(brasil))''')
md('''## 1. Qualidade e rastreabilidade
As contagens se referem a respostas por edição, não pessoas únicas em três anos. Somente duplicatas inteiramente idênticas são removidas. Salários malformados não são corrigidos por suposição; conflitos de IA são excluídos apenas do índice de uso.''')
code("""display(pd.read_csv(BASE/'resultados/qualidade.csv'))
display(pd.read_csv(BASE/'resultados/anomalias_salariais.csv'))
display(pd.read_csv(BASE/'resultados/dicionario_mapeamento.csv').head(12))""")
md('''## 2. Spark: mesmo contrato, implementação distribuída
O teste incluído usa `silver_one` e `gold_tables`, as mesmas funções chamadas pelo Glue Job. Ele confere todas as categorias e contagens dos resultados, além da escrita e releitura Parquet.
A saída abaixo é o relatório real do teste já realizado. Ative a flag para repetir o teste neste computador; é necessário Java e PySpark. O teste local não valida IAM, S3 remoto nem execução do Glue.''')
code("""REPETIR_TESTE_SPARK = False
if REPETIR_TESTE_SPARK:
    processo = subprocess.run([sys.executable, str(BASE/'codigos/validar_spark_local.py'),
                              str(BASE/'dados_originais'), str(BASE/'resultados')],
                              capture_output=True, text=True, check=True)
    print(processo.stdout)
print((BASE/'resultados/validacao_spark.txt').read_text())""")
md('''### Transformação Spark para uma edição — exemplo de uso
O código abaixo documenta o ponto de entrada para execução interativa em um notebook Spark. Mantê-lo desativado evita abrir outra sessão durante a leitura dos resultados. Na AWS, use o job completo para a publicação e a catalogação.''')
code("""EXECUTAR_EXEMPLO_SPARK = False
if EXECUTAR_EXEMPLO_SPARK:
    from pyspark.sql import SparkSession
    from glue_job import silver_one, gold_tables
    spark = SparkSession.builder.master('local[2]').appName('TechChallenge').getOrCreate()
    cfg = json.loads((BASE/'codigos/config_pipeline.json').read_text())
    frames = []
    for edicao, arquivo in cfg['fontes'].items():
        frame, qualidade = silver_one(spark, str(BASE/'dados_originais'/arquivo), edicao, cfg)
        frames.append(frame)
        print(qualidade)
    consolidada = frames[0]
    for frame in frames[1:]:
        consolidada = consolidada.unionByName(frame)
    for nome, tabela in gold_tables(consolidada, cfg).items():
        print(nome, tabela.count())
        tabela.show(5, truncate=False)
    spark.stop()""")
md('''## 3. Estrutura, diversidade e modelos de trabalho
Cada percentual tem o denominador da pergunta. As amostras não são um painel. Não extrapolamos para participação nacional no emprego.''')
code("""display(distribuicoes.query("dimensao == 'genero'"))
display(distribuicoes.query("edicao_pesquisa == '2025-2026' and dimensao == 'regiao'"))
for nome in ['01_genero','02_regioes','17_formacao','03_modelos','04_remoto']:
    display(Image(filename=str(BASE/'graficos'/(nome+'.png')), width=900))""")
md('''## 4. Perfis valorizados e remuneração
Medida: proporção em faixas iniciadas em R$ 12.001/mês ou superiores, entre salários válidos. Não se usa salário médio por ponto médio. Ranking apresentado com n mínimo de 30. Cargo, região e modelo de trabalho não demonstram efeito causal na remuneração.''')
code("""display(salarios.query("edicao_pesquisa == '2025-2026' and dimensao == 'cargo' and denominador >= 30").sort_values('percentual', ascending=False))
for nome in ['05_senioridade','06_cargos','07_salario_regiao','08_salario_modelo']:
    display(Image(filename=str(BASE/'graficos'/(nome+'.png')), width=900))
# Cruzamento adicional para examinar composição sem afirmar causalidade.
cruzamento = brasil.query("edicao_pesquisa == '2025-2026'").dropna(subset=['cargo','senioridade','salario_alto']).groupby(['cargo','senioridade']).salario_alto.agg(n='size', n_alto='sum', proporcao='mean').reset_index()
display(cruzamento[cruzamento.n.ge(30)].sort_values(['cargo','senioridade']))""")
md('''## 5. Tecnologias: distinguir uso e preferência
O bloco SQL/Python de 2025–2026 tem cabeçalho de preferência; o bloco cloud de 2023 também. Por cautela, usamos 2024 para adoção de SQL/Python e 2025–2026 para adoção de cloud/BI. Múltipla escolha: percentuais não precisam somar 100%.''')
code("""for nome in ['09_linguagens_2024','10_cloud','11_bi']:
    display(Image(filename=str(BASE/'graficos'/(nome+'.png')), width=900))""")
md('''## 6. IA: uso, financiamento, governança e impacto
Uso deriva das alternativas de uso positivas; respostas contraditórias com “não uso” ficam fora do denominador. O resultado com LLMs é percepção de respondentes do bloco de gestores, não ROI auditado nem contagem de empresas únicas.''')
code("""display(indicadores[indicadores.indicador.isin(['ia_usa','ia_paga_empresa','ia_centralizada'])])
for nome in ['12_ia','13_governanca','14_impacto']:
    display(Image(filename=str(BASE/'graficos'/(nome+'.png')), width=900))""")
md('''## 7. Recomendações para a instituição financeira
1. Calibrar faixas por cargo/senioridade e combinar contratação especializada com trilhas internas.
2. Testar flexibilidade e monitorar aceite de ofertas e retenção.
3. Monitorar representação e progressão por gênero, sem atribuir causalidade a diferenças brutas.
4. Capacitar SQL/Python, engenharia, qualidade de dados e cloud.
5. Financiar ferramentas aprovadas de IA e medir pilotos com baseline de tempo, custo e qualidade.

O plano de 90 dias é uma proposta executiva. Metas numéricas precisam de baseline interno; não foram inventadas a partir da pesquisa.''')
code("""for nome in ['15_atracao','16_financas']:
    display(Image(filename=str(BASE/'graficos'/(nome+'.png')), width=900))""")
md('''## 8. Execução cloud e entrega
Execute o job conforme o Guia Didático. Depois rode as consultas SQL no Athena, baixe os três agregados e compare com `reconciliar_athena.py`. Atualize os slides de status somente após comprovar a execução.

**Fontes:** enunciado e três CSVs fornecidos. Referências de dataset estão no JSON de proveniência; referências técnicas oficiais e limitações constam no guia. O resultado é descritivo da amostra, não uma estimativa censitária do mercado.''')
nb.cells=cells;nb.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.11'}}
nbf.write(nb,BASE/'Notebook_Analise.ipynb')
client=NotebookClient(nb,timeout=300,kernel_name='python3',resources={'metadata':{'path':str(BASE)}})
client.execute();nbf.write(nb,BASE/'Notebook_Analise.ipynb')
print('Guia Word e notebook executado com sucesso.')
