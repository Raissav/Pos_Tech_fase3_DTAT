"""Gera os gráficos e a apresentação executiva a partir das tabelas calculadas.
Executar após analise_local.py, a partir de qualquer diretório.
"""
from pathlib import Path
import json, textwrap, xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE,XL_LABEL_POSITION,XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
BASE=Path(__file__).resolve().parent.parent
R=BASE/'resultados'; G=BASE/'graficos';G.mkdir(exist_ok=True)
d=pd.read_csv(R/'distribuicoes.csv',dtype={'edicao_pesquisa':str});i=pd.read_csv(R/'indicadores.csv',dtype={'edicao_pesquisa':str});p=pd.read_csv(R/'salarios_segmentos.csv',dtype={'edicao_pesquisa':str});s=pd.read_parquet(R/'silver_local.parquet');b=s[s.vive_no_brasil.eq(1)]
E=['2023','2024','2025-2026']; LAST=E[-1]
NAVY='14283F';TEAL='007F86';ORANGE='EB8A23';GRAY='516276';LIGHT='F3F6FA';WHITE='FFFFFF';BLUE='5287BA'
COLORS=[TEAL,ORANGE,BLUE,'78948C']
charts={};slides_notes=[]
def dv(dim,cat,e=LAST):
 return float(d[(d.edicao_pesquisa==e)&(d.dimensao==dim)&(d.categoria==cat)].percentual.iloc[0])
def iv(metric,e=LAST):return float(i[(i.edicao_pesquisa==e)&(i.indicador==metric)].percentual.iloc[0])
def fmt(x):return f'{x:.1f}'.replace('.',',')+'%'
def chart_spec(key,cats,series,title,note,kind='bar'):
 charts[key]=dict(categories=list(cats),series={k:[float(v) for v in vals] for k,vals in series.items()},title=title,note=note,kind=kind)
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
 fig,ax=plt.subplots(figsize=(11,5.5)); fig.set_facecolor('white')
 if kind=='line':
  for k,(name,vals) in enumerate(series.items()):
   ax.plot(cats,vals,marker='o',label=name,color='#'+COLORS[k],linewidth=2.5)
   for x,v in zip(cats,vals):ax.annotate(fmt(v),(x,v),xytext=(0,8),textcoords='offset points',ha='center',fontsize=10)
  ax.set_ylim(0,110);ax.set_ylabel('% das respostas válidas');ax.legend(frameon=False)
 else:
  y=np.arange(len(cats));width=.7/len(series)
  for k,(name,vals) in enumerate(series.items()):
   offset=(k-(len(series)-1)/2)*width
   ax.barh(y+offset,vals,width,label=name,color='#'+COLORS[k])
   for yy,v in zip(y+offset,vals):ax.text(v+1,yy,fmt(v),va='center',fontsize=9)
  ax.set_yticks(y,[textwrap.fill(str(c),36) for c in cats]);ax.invert_yaxis();ax.set_xlim(0,112);ax.set_xlabel('% das respostas válidas')
  if len(series)>1:ax.legend(frameon=False,loc='lower right')
 for sp in ['top','right','left']:ax.spines[sp].set_visible(False)
 ax.grid(axis='x' if kind=='bar' else 'y',alpha=.15);ax.set_axisbelow(True)
 fig.suptitle(title,x=.03,ha='left',fontsize=15,fontweight='bold',color='#'+NAVY)
 fig.text(.03,.025,textwrap.fill(note,140),fontsize=8,color='#'+GRAY)
 fig.tight_layout(rect=[0,.09,1,.93]);fig.savefig(G/(key+'.png'),dpi=180);plt.close(fig)

chart_spec('01_genero',E,{'Feminino':[dv('genero','Feminino',e) for e in E]},'A participação feminina é menor nas edições mais recentes','Residentes no Brasil; n = 5.172 / 5.076 / 3.372. Inclui todas as categorias no denominador. Amostras independentes, não painel.', 'line')
regions=['Sudeste','Sul','Nordeste','Centro-oeste','Norte']
chart_spec('02_regioes',regions,{'2025–2026':[dv('regiao',c) for c in regions]},'O Sudeste concentra 64,4% das respostas com região informada','2025–2026; residentes no Brasil com região válida: n = 3.369. Não é estimativa de participação no emprego nacional.')
models=['Modelo 100% remoto','Modelo híbrido flexível (o funcionário tem liberdade para escolher quando estar no escritório presencialmente)','Modelo híbrido com dias fixos de trabalho presencial','Modelo 100% presencial']
labels=['100% remoto','Híbrido flexível','Híbrido com dias fixos','100% presencial']
chart_spec('03_modelos',labels,{'Atual':[dv('modelo_atual',c) for c in models],'Ideal':[dv('modelo_ideal',c) for c in models]},'A preferência por flexibilidade supera a prática atual','2025–2026; n = 3.123 em cada pergunta. Categorias mutuamente exclusivas dentro de cada pergunta.')
chart_spec('04_remoto',E,{'100% remoto atual':[dv('modelo_atual',models[0],e) for e in E]},'O remoto integral perde espaço na composição das amostras','Residentes com modelo atual informado; n = 4.653 / 4.734 / 3.123. Variação descritiva entre amostras.', 'line')
q=p[(p.edicao_pesquisa==LAST)&(p.dimensao=='senioridade')].set_index('categoria');cats=['Júnior','Pleno','Sênior','Especialista/Staff+']
chart_spec('05_senioridade',cats,{'Faixa ≥ R$ 12.001/mês':[q.loc[c,'percentual'] for c in cats]},'Senioridade diferencia fortemente a distribuição salarial','2025–2026; n por grupo: 510 / 755 / 824 / 339. Faixa reportada, sem média imputada. Staff+ aparece como categoria nesta edição.')
q=p[(p.edicao_pesquisa==LAST)&(p.dimensao=='cargo')&(p.denominador>=30)].sort_values('percentual',ascending=False).head(6)
role_labels=['ML / AI Engineer','Analytics Engineer','Engenharia / Arquitetura de Dados','Ciência de Dados','Desenvolvimento de Software','Análise de Dados']
chart_spec('06_cargos',role_labels,{'Faixa ≥ R$ 12.001/mês':q.percentual},'ML/IA e engenharia têm maior concentração nas faixas altas','2025–2026; n dos cargos: '+ ' / '.join(map(str,q.denominador)) +'. Ranking elegível n ≥ 30; não controla senioridade e não mede vagas.')
q=p[(p.edicao_pesquisa==LAST)&(p.dimensao=='regiao')].set_index('categoria')
chart_spec('07_salario_regiao',regions,{'Faixa ≥ R$ 12.001/mês':[q.loc[c,'percentual'] for c in regions]},'As regiões diferem, mas há forte assimetria amostral','2025–2026; n: Sudeste 2.023; Sul 510; Nordeste 329; Centro-oeste 221; Norte 36. Comparação não ajustada.')
q=p[(p.edicao_pesquisa==LAST)&(p.dimensao=='modelo_atual')].set_index('categoria')
chart_spec('08_salario_modelo',labels,{'Faixa ≥ R$ 12.001/mês':[q.loc[c,'percentual'] for c in models]},'Remoto e híbrido flexível concentram faixas mais altas','2025–2026; n: remoto 1.250; híbrido flexível 603; híbrido fixo 619; presencial 650. Associação, não efeito causal do modelo.')
chart_spec('09_linguagens_2024',['SQL','Python'],{'Uso no trabalho em 2024':[iv('sql','2024'),iv('python','2024')]},'SQL e Python sustentam a trilha básica de capacitação','2024; n = 3.502 respostas válidas por item. Múltipla escolha. Em 2025–2026, o cabeçalho indica preferência; não comparar como adoção.')
chart_spec('10_cloud',['AWS','Azure','GCP'],{'Uso no dia a dia':[iv('aws'),iv('azure'),iv('gcp')]},'AWS lidera entre as três clouds comparadas nesta amostra','2025–2026; n = 2.033 por item; múltipla escolha. Cloud em 2023 tem cabeçalho de preferência; série temporal não utilizada.')
chart_spec('11_bi',['Power BI','Tableau'],{'Uso no dia a dia':[iv('powerbi'),iv('tableau')]},'Power BI tem ampla presença entre os respondentes','2025–2026; n = 2.043 por item; múltipla escolha. Comparação destas ferramentas, não ranking exaustivo de todas as opções.')
chart_spec('12_ia',E,{'Uso declarado de IA':[iv('ia_usa',e) for e in E],'Empresa paga solução':[iv('ia_paga_empresa',e) for e in E]},'O uso declarado de IA se amplia; o financiamento também','Uso: n = 3.671 / 3.518 / 2.038, após excluir conflitos. Empresa paga: n = 3.697 / 3.531 / 2.043. Respostas de técnicos, não toda a amostra.', 'line')
chart_spec('13_governanca',E,{'Uso descentralizado':[iv('ia_descentralizada',e) for e in E],'Direcionamento centralizado':[iv('ia_centralizada',e) for e in E]},'A governança cresce, mas o uso descentralizado permanece','Bloco técnico; residentes; n = 3.697 / 3.531 / 2.043 por item. Alternativas podem coexistir, logo não somam 100%.', 'line')
q=d[(d.edicao_pesquisa==LAST)&(d.dimensao=='ia_resultado')].sort_values('n',ascending=False)
chart_spec('14_impacto',['Pilotos com pouco resultado','Produção com resultados','Investigação / planejamento','Sem projeto iniciado','Não sabe opinar'],{'Percepção dos gestores':q.percentual},'Uso difundido não significa impacto de negócio comprovado','2025–2026; bloco de gestores; n = 616 respostas válidas. Percepção declarada; não empresas únicas e não ROI auditado.')
chart_spec('15_atracao',['Remuneração','Flexibilidade remota','Plano de carreira'],{'Critério de escolha':[iv('criterio_salario'),iv('criterio_flexibilidade'),iv('criterio_carreira')]},'A proposta de valor deve combinar salário, flexibilidade e carreira','2025–2026; n = 3.123 por item. Múltipla escolha; critérios podem coexistir.')
q=d[(d.edicao_pesquisa==LAST)&(d.dimensao=='escolaridade')].sort_values('n',ascending=False)
chart_spec('17_formacao',q.categoria,{'Escolaridade declarada':q.percentual},'A formação avançada é frequente na amostra','2025–2026; residentes no Brasil; n = 3.372, incluindo recusa. Escolaridade reportada não prova competência nem efeito causal na remuneração.')
# Recorte financeiro e cruzamentos com n explícito.
rows=[]
for name,g in b[b.edicao_pesquisa.eq(LAST)&b.setor.notna()&b.salario_alto.notna()].groupby(b.setor.eq('Finanças ou Bancos')):
 rows.append({'segmento':'Finanças ou Bancos' if name else 'Outros setores','n':len(g),'n_salario_alto':int(g.salario_alto.sum()),'percentual':100*g.salario_alto.mean()})
f=pd.DataFrame(rows);f.to_csv(R/'benchmark_financeiro.csv',index=False)
chart_spec('16_financas',f.segmento,{'Faixa ≥ R$ 12.001/mês':f.percentual},'O setor financeiro exige uma referência salarial competitiva','2025–2026; residentes; com setor e salário válidos. n: '+ '; '.join(f'{r.segmento}: {r.n}' for r in f.itertuples())+'. Comparação não ajustada por composição.')
q=b[b.edicao_pesquisa.eq(LAST)&b.salario_alto.notna()&b.cargo.notna()&b.senioridade.notna()].groupby(['cargo','senioridade']).salario_alto.agg(['size','sum','mean']).reset_index();q=q[q['size']>=30];q.to_csv(R/'salario_cargo_senioridade.csv',index=False)
json.dump(charts,open(R/'dados_graficos.json','w'),ensure_ascii=False,indent=2)

# Diagrama editável compatível com diagrams.net / Draw.io.
nodes=[('b','S3 | Bronze\nCSVs originais por edição',40,90,220,85),('j','Glue Job | Spark\nLeitura, qualidade e harmonização',310,90,250,85),('s','S3 | Silver\nParquet Snappy + edição',610,90,230,85),('g','S3 | Gold\nIndicadores e distribuições',890,90,235,85),('c','Glue Data Catalog\nTabelas + partições via Job',610,270,230,85),('a','Athena | SQL\nConsulta e reconciliação',890,270,235,85),('v','Python / gráficos\nConsumo analítico local',890,450,235,85),('x','PowerPoint / PDF\nStorytelling executivo',610,450,230,85),('o','CloudWatch + IAM\nLogs e permissões do Lab',310,270,250,85)]
mx=ET.Element('mxfile',host='app.diagrams.net');diagram=ET.SubElement(mx,'diagram',name='Arquitetura AWS');model=ET.SubElement(diagram,'mxGraphModel',dx='1400',dy='900',page='1',pageWidth='1200',pageHeight='760');root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
for id,label,x,y,w,h in nodes:
 c=ET.SubElement(root,'mxCell',id=id,value=label,style='rounded=1;whiteSpace=wrap;html=0;fillColor=#F3F6FA;strokeColor=#007F86;fontColor=#14283F;fontSize=16;',vertex='1',parent='1');ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
for n,(a,z) in enumerate([('b','j'),('j','s'),('s','g'),('j','c'),('s','c'),('g','a'),('c','a'),('a','v'),('v','x'),('o','j')]):
 c=ET.SubElement(root,'mxCell',id='e'+str(n),style='edgeStyle=orthogonalEdgeStyle;rounded=0;endArrow=block;strokeColor=#516276;',edge='1',parent='1',source=a,target=z);ET.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
for id,text,x,y,w,h in [('title','Arquitetura alvo | Tech Challenge Fase 3',40,20,1100,45),('status','Status: bucket e conversão Glue informados pelo aluno. Pipeline aprimorado validado localmente. Execução e evidências AWS pendentes.',40,610,1085,75)]:
 c=ET.SubElement(root,'mxCell',id=id,value=text,style='text;html=0;whiteSpace=wrap;fontSize=18;fontColor=#14283F;',vertex='1',parent='1');ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
ET.ElementTree(mx).write(BASE/'Arquitetura_AWS.drawio',encoding='utf-8',xml_declaration=True)

prs=Presentation();prs.slide_width=Inches(13.333);prs.slide_height=Inches(7.5)
prs.core_properties.title='Mercado brasileiro de Dados e IA | Tech Challenge Fase 3';prs.core_properties.author='Equipe do Tech Challenge'
def rgb(c):return RGBColor.from_string(c)
def txt(sl,x,y,w,h,text,size=20,color=NAVY,bold=False):
 sh=sl.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h));tf=sh.text_frame;tf.word_wrap=True
 for j,line in enumerate(text.split('\n')):
  pa=tf.paragraphs[0] if j==0 else tf.add_paragraph();pa.text=line;pa.space_after=Pt(10)
  for run in pa.runs:
   run.font.name='Aptos';run.font.size=Pt(size);run.font.bold=bold;run.font.italic=False;run.font.color.rgb=rgb(color)
 return sh

def slide(title,kicker='EVIDÊNCIAS → DECISÃO',dark=False):
 sl=prs.slides.add_slide(prs.slide_layouts[6]);sl.background.fill.solid();sl.background.fill.fore_color.rgb=rgb(NAVY if dark else WHITE)
 txt(sl,.5,.24,12,.3,kicker,11,ORANGE,True);txt(sl,.5,.72,12.3,1.0,title,29,WHITE if dark else NAVY,True)
 txt(sl,.5,7.05,11,.25,'STATE OF DATA BRASIL  |  2023 • 2024 • 2025–2026  |  TECH CHALLENGE — FASE 3',9,'CAD6E4' if dark else GRAY)
 txt(sl,12.2,7.03,.6,.3,f'{len(prs.slides):02d}',10,ORANGE,True)
 return sl

def notes(sl,text):
 sl.notes_slide.notes_text_frame.text=text
 slides_notes.append({'slide':len(prs.slides),'titulo':sl.shapes[1].text if len(sl.shapes)>1 else '', 'fala':text})

def card(sl,x,y,w,title,body,dark=False):
 sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(1.7));sh.fill.solid();sh.fill.fore_color.rgb=rgb('213D57' if dark else LIGHT);sh.line.fill.background()
 txt(sl,x+.18,y+.12,w-.36,.48,title,25,ORANGE if dark else TEAL,True);txt(sl,x+.18,y+.7,w-.36,.8,body,17,WHITE if dark else NAVY)

def bullets(sl,items,x=.6,y=1.95,w=11.9,size=22):
 return txt(sl,x,y,w,min(4.8,6.8-y),'\n'.join('• '+t for t in items),size)

def addchart(sl,key,x=.6,y=1.95,w=8.1,h=4.5):
 sp=charts[key];cd=CategoryChartData();cd.categories=sp['categories']
 for name,vals in sp['series'].items():cd.add_series(name,vals)
 kind=XL_CHART_TYPE.LINE_MARKERS if sp['kind']=='line' else XL_CHART_TYPE.BAR_CLUSTERED
 ch=sl.shapes.add_chart(kind,Inches(x),Inches(y),Inches(w),Inches(h),cd).chart
 ch.has_legend=len(sp['series'])>1
 if ch.has_legend:
  ch.legend.position=XL_LEGEND_POSITION.BOTTOM;ch.legend.include_in_layout=False;ch.legend.font.size=Pt(12)
 ch.chart_style=10
 ch.value_axis.minimum_scale=0;ch.value_axis.maximum_scale=110;ch.value_axis.tick_labels.font.size=Pt(11);ch.value_axis.tick_labels.number_format='0"%"'
 ch.category_axis.tick_labels.font.size=Pt(13)
 if sp['kind']=='bar':ch.category_axis.reverse_order=True
 for k,se in enumerate(ch.series):
  se.format.line.color.rgb=rgb(COLORS[k]);se.format.fill.solid();se.format.fill.fore_color.rgb=rgb(COLORS[k])
  if sp['kind']=='line':se.format.line.width=Pt(2.7)
 plot=ch.plots[0];plot.has_data_labels=True;plot.data_labels.font.size=Pt(12);plot.data_labels.number_format='0.0"%"'
 if sp['kind']=='bar':plot.data_labels.position=XL_LABEL_POSITION.OUTSIDE_END
 txt(sl,.6,6.55,12,.39,sp['note'],11,GRAY)
 return ch

def chartslide(title,key,insight,action):
 sl=slide(title);addchart(sl,key);txt(sl,9.05,2.0,3.65,2.0,insight,23,TEAL,True);txt(sl,9.05,4.2,3.65,2.0,action,19)
 notes(sl,charts[key]['title']+'. '+charts[key]['note']+' Interpretação: '+insight+' Recomendação: '+action)
 return sl

sl=slide('Dados e IA no Brasil:\nda evidência à estratégia de expansão','CONSULTORIA ESTRATÉGICA  |  INSTITUIÇÃO FINANCEIRA',True)
txt(sl,.6,3.1,11.5,1.1,'Contratar com critério. Capacitar com foco.\nTransformar adoção de IA em resultado mensurável.',27,WHITE)
card(sl,.6,5.0,3.85,'3 edições','2023 • 2024 • 2025–2026',True);card(sl,4.75,5,3.85,'13.620','Respostas residentes no Brasil, após deduplicação',True);card(sl,8.9,5,3.85,'AWS + Spark','Engenharia, Analytics e storytelling',True)
notes(sl,'Apresente os integrantes e a turma verbalmente. Esta entrega combina análise verificada dos arquivos e arquitetura proposta para execução no AWS Academy Lab. A unidade de análise é resposta por edição, não pessoa única ao longo do tempo.')
sl=slide('O que está comprovado — e o que falta executar','TRANSPARÊNCIA DA ENTREGA')
card(sl,.6,2,3.85,'Informado pelo aluno','Bucket no S3 e conversão CSV → Parquet no Glue.')
card(sl,4.75,2,3.85,'Verificado localmente','Análise dos CSVs, qualidade e paridade Pandas × Spark.')
card(sl,8.9,2,3.85,'Pendente no Lab','Executar job aprimorado, catálogo e consultas; coletar evidências.')
txt(sl,.7,4.25,11.8,1.6,'Não há execução AWS simulada ou screenshot fabricado.\nO guia explica como completar e comprovar cada requisito antes de entregar.',23)
notes(sl,'A versão inicial do usuário foi lida. O pipeline aprimorado foi testado em Spark local 3.5.6. IAM, S3 remoto, integração Glue e Athena só podem ser validados no Lab do grupo. Atualize esta lâmina após execução real, informando data e ID do job.')
sl=slide('Quatro sinais orientam a decisão executiva')
card(sl,.6,2,5.85,'85,2%','Preferem remoto ou híbrido flexível em 2025–2026.')
card(sl,6.85,2,5.85,'22,0%','Participação feminina entre residentes em 2025–2026.')
card(sl,.6,4.05,5.85,'98,1%','Uso de IA no bloco técnico, após excluir respostas conflitantes.')
card(sl,6.85,4.05,5.85,'27,6%','Respondentes do bloco de gestores relatam IA em produção com resultados.')
txt(sl,.6,6.35,12,.45,'Denominadores distintos: modelo n=3.123; gênero n=3.372; uso IA n=2.038; impacto n=616. Resultados amostrais.',12,GRAY)
notes(sl,'Não contraponha os 98,1% e 27,6% como um funil com os mesmos respondentes: são perguntas e universos distintos. A leitura conjunta sugere a necessidade de medir valor, sem provar causalidade.')
sl=slide('Arquitetura: preservar, harmonizar e disponibilizar','AWS ACADEMY LAB  |  ARQUITETURA ALVO')
# Diagrama nativo da apresentação, com fluxo equivalente ao Draw.io.
positions={'Bronze':(.65,2.1),'Glue / Spark':(3.8,2.1),'Silver':(6.95,2.1),'Gold':(10.1,2.1),'Catálogo':(6.95,4.15),'Athena':(10.1,4.15),'Logs / IAM':(3.8,4.15),'Executivo':(.65,4.15)}
labels2={'Bronze':'S3\nCSVs originais','Glue / Spark':'ETL + qualidade\nDeduplicação e mapeamento','Silver':'S3 | Parquet\nPartição por edição','Gold':'S3 | Parquet\nIndicadores analíticos','Catálogo':'Glue Data Catalog\nTabelas e partições','Athena':'SQL → gráficos\nConsumo analítico','Logs / IAM':'CloudWatch\nLogs e permissões','Executivo':'PowerPoint / PDF\nGráficos locais'}
for name,(x,y) in positions.items():
 sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x),Inches(y), Inches(2.6),Inches(1.35));sh.fill.solid();sh.fill.fore_color.rgb=rgb(LIGHT);sh.line.color.rgb=rgb(TEAL)
 txt(sl,x+.12,y+.1,2.36,.35,name,20,TEAL,True);txt(sl,x+.12,y+.55,2.36,.75,labels2[name],15)
for x1,y1,x2,y2 in [(3.25,2.77,3.8,2.77),(6.4,2.77,6.95,2.77),(9.55,2.77,10.1,2.77),(8.25,3.45,8.25,4.15),(11.4,3.45,11.4,4.15),(9.55,4.8,10.1,4.8),(5.1,4.15,5.1,3.45),(11.4,5.5,11.4,5.85),(11.4,5.85,1.95,5.85),(1.95,5.85,1.95,5.5)]:
 co=sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1), Inches(y1), Inches(x2), Inches(y2));co.line.color.rgb=rgb(ORANGE);co.line.width=Pt(2)
txt(sl,.7,6.05,12,.65,'Arquivo Draw.io editável acompanha a entrega. Pipeline aprimorado e catálogo: executar no Lab.\nConsumo local dos resultados não exige ferramenta de dashboard.',14,GRAY)
notes(sl,'Explique que as conversões antigas não serão apagadas. A Bronze usa o prefixo de entrada existente. A nova saída usa um snapshot por RUN_ID. O job cataloga via API Glue e registra as três partições; não depende de crawler. IAM e CloudWatch são controles de execução, a confirmar no Lab.')
sl=slide('Qualidade: corrigir sem inventar respostas')
rows=[['Edição','CSV','Duplicatas','Silver','Brasil'],['2023','5.293','0','5.293','5.172'],['2024','5.217','2','5.215','5.076'],['2025–2026','3.495','1','3.494','3.372']]
table=sl.shapes.add_table(4,5,Inches(.65),Inches(1.95),Inches(12),Inches(2.0)).table
for r,row in enumerate(rows):
 for c,val in enumerate(row):
  cell=table.cell(r,c);cell.text=val;cell.fill.solid();cell.fill.fore_color.rgb=rgb(NAVY if r==0 else LIGHT)
  for pa in cell.text_frame.paragraphs:
   for run in pa.runs:run.font.name='Aptos';run.font.size=Pt(18);run.font.bold=r==0;run.font.italic=False;run.font.color.rgb=rgb(WHITE if r==0 else NAVY)
bullets(sl,['14.002 respostas preservadas na Silver; 13.620 residentes no Brasil usados nas análises.','2 faixas salariais malformadas: preservar original e excluir apenas de cálculos salariais.','44 conflitos de IA: “não uso” + alternativa de uso; excluir somente do índice de uso.'],y=4.35,size=19)
notes(sl,'Duplicatas são registros inteiramente idênticos: 2 em 2024 e 1 em 2025–2026. Não há IDs conflitantes após essa remoção. As 44 contradições abrangem todos os residentes e não residentes; entre residentes são 26, 13 e 5. As anomalias salariais estão listadas no CSV de auditoria. Não imputamos a faixa presumida.')
sl=slide('Comparabilidade é parte do resultado, não uma nota de rodapé')
bullets(sl,['Amostras independentes: não acompanhamos as mesmas pessoas ao longo do tempo.','Indicadores descrevem respondentes residentes no Brasil; cada pergunta tem seu denominador.','SQL/Python: uso no trabalho em 2023–2024; cabeçalho indica preferência em 2025–2026.','Cloud: cabeçalho de preferência em 2023; adoção comparada somente em 2024–2026.','Especialista/Staff+ surge como categoria em 2025–2026: não inferir queda de sêniores.','Salários nominais por faixa: sem salário médio estimado, sem ajuste inflacionário.'],size=20)
notes(sl,'Sem desenho amostral e pesos fornecidos, não extrapolamos percentuais como estimativas representativas do emprego brasileiro. A pesquisa mede tecnologias declaradas, não procura por vagas. As diferenças de remuneração não foram ajustadas por composição e não demonstram discriminação ou causalidade.')
chartslide('Estrutura: concentração regional e competição por talentos','02_regioes','64,4% no Sudeste; 19,0% no setor de Finanças/Bancos.','Ampliar recrutamento nacional e avaliar disponibilidade por cargo, não só localização.')
chartslide('Formação: combinar base acadêmica e aprendizagem aplicada','17_formacao','56,8% informam pós-graduação, mestrado ou doutorado.','Avaliar entregas práticas e capacitação contínua, sem transformar diploma em único filtro.')
chartslide('Diversidade: participação feminina recua na amostra','01_genero','24,5% → 22,0%\nVariação de −2,5 p.p. entre edições.','Revisar etapas de seleção e progressão; acompanhar representação por senioridade.')
chartslide('Trabalho remoto: a composição está mudando','04_remoto','46,3% → 40,1%\nVariação de −6,2 p.p. no remoto integral.','Não confundir mudança da amostra com mudança das mesmas pessoas ou empresas.')
chartslide('Flexibilidade é um componente da proposta de valor','03_modelos','85,2% preferem remoto ou híbrido flexível; 59,4% trabalham nesses formatos.','Testar política de flexibilidade compatível com as atividades e medir retenção.')
chartslide('Remuneração: diferenciar faixas por senioridade','05_senioridade','83,2% dos especialistas/Staff+ estão em faixas a partir de R$ 12.001.','Definir trilhas técnicas e critérios de progressão; não usar uma faixa única para toda a área.')
chartslide('Perfis valorizados: ML/IA e engenharia se destacam','06_cargos','63,1% em ML/IA versus 16,5% em Análise de Dados.','Combinar contratação sênior com formação interna. Cargo sozinho não explica o salário.')
chartslide('Regiões: interpretar diferenças com tamanho de amostra','07_salario_regiao','Sudeste: 44,6%\nNordeste: 31,6% em faixas altas.','Não ranquear o Norte como mercado equivalente: apenas 36 respostas salariais válidas.')
chartslide('Modelo de trabalho e salário: associação, não causa','08_salario_modelo','Remoto: 50,6%\nPresencial: 21,2% em faixas altas.','Comparar também cargo e senioridade antes de definir política salarial ou de presença.')
chartslide('Capacitação: fundamentos antes de especialização','09_linguagens_2024','SQL: 87,7%\nPython: 81,8% de uso declarado em 2024.','Priorizar SQL, Python e qualidade de dados; medir competência por entregas práticas.')
chartslide('Cloud: AWS é aderente ao cenário observado','10_cloud','AWS: 48,1% entre respondentes válidos de 2025–2026.','Usar S3, Glue, Spark e Athena no projeto; evitar concluir superioridade técnica pelo percentual.')
chartslide('Analytics: visualização conecta dados à decisão','11_bi','Power BI: 59,0%\nTableau: 13,4% na amostra.','Capacitar storytelling e métricas de negócio; dashboard continua opcional nesta entrega.')
chartslide('IA: adoção declarada se aproxima da saturação','12_ia','98,1% no bloco técnico; 42,4% relatam solução paga pela empresa.','Oferecer ferramentas aprovadas e medir uso com qualidade, custo e resultado — não apenas licenças.')
chartslide('Governança: centralizar sem bloquear a experimentação','13_governanca','Direcionamento centralizado: 10,5% → 35,9%.','Definir catálogo de ferramentas, orientações de dados e revisão humana para os pilotos.')
chartslide('Impacto: produção com resultado ainda é uma minoria','14_impacto','27,6% relatam produção com resultado; 38,5% citam pilotos com pouco resultado.','Priorizar casos com baseline e critérios de sucesso. Não há ROI auditado nesta pesquisa.')
chartslide('Contratação e retenção: uma proposta de valor integrada','15_atracao','83,2% citam salário; 56,7% citam flexibilidade.','Combinar remuneração competitiva, flexibilidade e trilhas de carreira explícitas.')
chartslide('Instituição financeira: orçamento precisa refletir o mercado','16_financas','Finanças/Bancos concentram 19,0% das respostas com setor informado.','Calibrar orçamento com cargo e senioridade; validar referências com recrutamento real.')
sl=slide('Plano de 90 dias: contratar, capacitar e provar valor','RECOMENDAÇÕES — PROPOSTA, NÃO RESULTADO OBSERVADO')
for x,title,body in [(.65,'0–30 dias','RH + Dados\nMapear cargos, faixas e lacunas.\nDefinir baseline de contratação e diversidade.'),(4.85,'31–60 dias','Engenharia + Analytics\nTrilha SQL/Python/AWS.\nTestar flexibilidade e 2 pilotos de IA com avaliação.'),(9.05,'61–90 dias','Negócio + Dados\nAvaliar qualidade, custo e tempo.\nEscalar apenas casos com resultado validado.')]:
 sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(x),Inches(2.05),Inches(3.65),Inches(3.75));sh.fill.solid();sh.fill.fore_color.rgb=rgb(LIGHT);sh.line.fill.background();txt(sl,x+.15,2.25,3.35,.6,title,27,TEAL,True);txt(sl,x+.15,3.0,3.35,2.7,body,20)
txt(sl,.7,6.15,12,.55,'Indicadores propostos: tempo de contratação • aceite de oferta • progressão por gênero • entregas de capacitação • tempo/custo/qualidade dos pilotos',15,GRAY)
notes(sl,'Os prazos são uma proposta executiva. Não são metas derivadas estatisticamente da pesquisa. Estabelecer valores-alvo após baseline interno. IA em instituição financeira demanda avaliação de segurança e revisão pelos responsáveis internos; não há parecer jurídico nesta entrega.')
sl=slide('Critério de conclusão: uma análise rastreável e uma execução comprovada','CHECKLIST FINAL DE ENTREGA')
bullets(sl,['Apresentação executiva: gráficos, limitações e recomendações baseadas nos arquivos.','Diagrama editável: abrir no Draw.io e salvar a versão final do grupo.','Códigos e notebook: transformação, qualidade, catálogo, SQL e gráficos.','Lab: job concluído, tabelas no catálogo e resultados reconciliados no Athena.','Evidências: screenshots reais, ID do job e exports das consultas.','Identificação: incluir integrantes e revisar esta lâmina e o status após executar.'],size=21)
notes(sl,'Conclua reforçando a cadeia de valor: dados preservados, processamento auditável e decisões contextualizadas. A entrega cloud só estará completa com a execução real e suas evidências. O teste local comparou 290 linhas de distribuições, 45 indicadores e 159 recortes salariais entre Pandas e Spark, mais escrita e releitura Parquet de 14.002 linhas.')
prs.save(BASE/'Apresentacao_Executiva.pptx')
json.dump(slides_notes,open(R/'roteiro_apresentacao.json','w'),ensure_ascii=False,indent=2)
# Roteiro textual para ensaio.
with open(BASE/'Roteiro_de_Apresentacao.md','w') as h:
 h.write('# Roteiro de apresentação — 15 a 20 minutos\n\nSelecione 12–15 slides centrais para uma fala curta; preserve os demais como apoio técnico. Não declare execução AWS antes de realizá-la.\n\n')
 for r in slides_notes:h.write(f"## Slide {r['slide']:02d} — {r['titulo']}\n\n{r['fala']}\n\n")
print('Apresentação:',len(prs.slides),'slides; gráficos:',len(charts))
