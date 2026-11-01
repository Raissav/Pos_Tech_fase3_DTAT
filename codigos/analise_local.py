"""Reproduz a análise local dos CSVs. Não substitui a execução AWS.
Uso: python analise_local.py --entrada /pasta/csvs --saida /pasta/resultados
"""
import argparse,json,re,hashlib
from pathlib import Path
import pandas as pd
import numpy as np
BASE=Path(__file__).parent
BINARY=['pcd','vive_no_brasil','gestor','satisfeito','criterio_salario','criterio_flexibilidade','criterio_carreira','sql','python','aws','gcp','azure','powerbi','tableau','ia_descentralizada','ia_centralizada','ia_nao_usa','ia_gratuita','ia_paga_pessoa','ia_paga_empresa','ia_copilot']
DIMS=['genero','regiao','escolaridade','situacao_trabalho','setor','cargo','senioridade','modelo_atual','modelo_ideal','faixa_salarial','ia_prioridade','ia_resultado']
METRICS=['ia_usa','ia_paga_empresa','ia_copilot','ia_descentralizada','ia_centralizada','criterio_salario','criterio_flexibilidade','criterio_carreira','sql','python','aws','gcp','azure','powerbi','tableau']
SALARIOS=['Menos de R$ 1.000/mês','de R$ 1.001/mês a R$ 2.000/mês','de R$ 2.001/mês a R$ 3.000/mês','de R$ 3.001/mês a R$ 4.000/mês','de R$ 4.001/mês a R$ 6.000/mês','de R$ 6.001/mês a R$ 8.000/mês','de R$ 8.001/mês a R$ 12.000/mês','de R$ 12.001/mês a R$ 16.000/mês','de R$ 16.001/mês a R$ 20.000/mês','de R$ 20.001/mês a R$ 25.000/mês','de R$ 25.001/mês a R$ 30.000/mês','de R$ 30.001/mês a R$ 40.000/mês','Acima de R$ 40.001/mês']
def gold(s):
 b=s[s.vive_no_brasil.eq(1)].copy(); dist=[]; rates=[]; pay=[]
 for e,g in b.groupby('edicao_pesquisa'):
  for c in DIMS:
   v=g[c].dropna(); den=len(v)
   for cat,n in v.value_counts().items():dist.append([e,c,cat,int(n),den,100*n/den])
  for c in METRICS:
   v=g[c].dropna(); den=len(v); n=int(v.sum())
   rates.append([e,c,n,den,100*n/den if den else np.nan])
  for dim in ['cargo','senioridade','regiao','modelo_atual','genero','setor']:
   q=g[g[dim].notna() & g.salario_alto.notna()]
   for cat,h in q.groupby(dim):
    n=len(h); a=int(h.salario_alto.sum());pay.append([e,dim,cat,a,n,100*a/n])
 return (pd.DataFrame(dist,columns=['edicao_pesquisa','dimensao','categoria','n','denominador','percentual']),pd.DataFrame(rates,columns=['edicao_pesquisa','indicador','n','denominador','percentual']),pd.DataFrame(pay,columns=['edicao_pesquisa','dimensao','categoria','n_salario_alto','denominador','percentual']))
def run(entrada,saida):
 saida=Path(saida);saida.mkdir(parents=True,exist_ok=True)
 m=json.load(open(BASE/'mapeamento.json')); fs=json.load(open(BASE/'fontes.json')); frames=[];dq=[];hashes={}
 for e,mp in m.items():
  p=Path(entrada)/fs[e];raw=pd.read_csv(p,dtype=str,keep_default_na=False);n=len(raw)
  hashes[fs[e]]=hashlib.sha256(p.read_bytes()).hexdigest()
  assert set(mp.values()).issubset(raw.columns)
  r=raw.drop_duplicates(); x=pd.DataFrame({k:r[c].str.strip().replace('',None) for k,c in mp.items()})
  assert x.id_resposta.notna().all() and not x.id_resposta.duplicated().any(),f'ID inválido/conflitante: {e}'
  for c in BINARY:
   v=x[c].str.lower(); assert v.dropna().isin(['1','0','true','false','sim','não','nao','prefiro não informar']).all(),(e,c)
   x[c]=v.map({'1':1,'true':1,'sim':1,'0':0,'false':0,'não':0,'nao':0})
  x['idade']=pd.to_numeric(x.idade,errors='coerce')
  x['idade_invalida']=x.idade.notna() & ~x.idade.between(14,100)
  x.loc[x.idade_invalida,'idade']=np.nan
  x['faixa_salarial_original']=x.faixa_salarial
  x['salario_anomalo']=x.faixa_salarial.notna() & ~x.faixa_salarial.isin(SALARIOS)
  x.loc[x.salario_anomalo,'faixa_salarial']=None
  x['salario_alto']=x.faixa_salarial.map({v:int(i>=7) for i,v in enumerate(SALARIOS)})
  opts=['ia_gratuita','ia_paga_pessoa','ia_paga_empresa','ia_copilot']
  known=x[opts+['ia_nao_usa']].notna().any(axis=1)
  use=x[opts].eq(1).any(axis=1)
  conflict=use & x.ia_nao_usa.eq(1)
  x['ia_resposta_conflitante']=conflict
  x['ia_usa']=np.where(known & ~conflict,use.astype(int),np.nan)
  if 'ia_resultado' not in x:x['ia_resultado']=None
  x['edicao_pesquisa']=e; x['arquivo_origem']=fs[e]
  x['respondente_chave']=x.id_resposta.map(lambda z:hashlib.sha256((e+'|'+z).encode()).hexdigest())
  # Não exportar o identificador original na Silver analítica.
  x=x.drop(columns='id_resposta')
  dq.append(dict(edicao=e,linhas_csv=n,colunas_csv=len(raw.columns),duplicatas_exatas=n-len(r),linhas_silver=len(x),residentes_brasil=int(x.vive_no_brasil.eq(1).sum()),salarios_anomalos=int(x.salario_anomalo.sum()),ia_conflitante=int(conflict.sum()),idades_invalidas=int(x.idade_invalida.sum())))
  frames.append(x)
 s=pd.concat(frames,ignore_index=True)
 s.to_parquet(saida/'silver_local.parquet',index=False)
 for name,df in zip(['distribuicoes','indicadores','salarios_segmentos'],gold(s)):df.to_csv(saida/f'{name}.csv',index=False)
 pd.DataFrame(dq).to_csv(saida/'qualidade.csv',index=False)
 s.isna().groupby(s.edicao_pesquisa).sum().T.to_csv(saida/'nulos_por_edicao.csv')
 json.dump(hashes,open(saida/'sha256_fontes.json','w'),indent=2)
 an=s[s.salario_anomalo][['edicao_pesquisa','faixa_salarial_original','arquivo_origem']]
 an.to_csv(saida/'anomalias_salariais.csv',index=False)
 print(pd.DataFrame(dq).to_string(index=False));return s
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--entrada',required=True);a.add_argument('--saida',required=True);args=a.parse_args();run(args.entrada,args.saida)
