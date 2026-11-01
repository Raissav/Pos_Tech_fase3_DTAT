"""Compare os exports reais do Athena com os resultados locais, sem alterar nenhum deles.
Uso: python codigos/reconciliar_athena.py --pasta evidencias_aws
Salvar os SELECT * como distribuicoes.csv, indicadores.csv e salarios_segmentos.csv nessa pasta.
"""
import argparse
from pathlib import Path
import pandas as pd
p=argparse.ArgumentParser();p.add_argument('--pasta',required=True);a=p.parse_args();root=Path(__file__).resolve().parent.parent
logs=[]
for name in ['distribuicoes','indicadores','salarios_segmentos']:
 local=pd.read_csv(root/'resultados'/(name+'.csv'),dtype={'edicao_pesquisa':str})
 aws=pd.read_csv(Path(a.pasta)/(name+'.csv'),dtype={'edicao_pesquisa':str})
 keys=['edicao_pesquisa','indicador'] if name=='indicadores' else ['edicao_pesquisa','dimensao','categoria']
 aws=aws[local.columns].sort_values(keys).reset_index(drop=True);local=local.sort_values(keys).reset_index(drop=True)
 pd.testing.assert_frame_equal(local,aws,check_dtype=False,check_exact=False,atol=1e-7,rtol=1e-7)
 logs.append(f'PASS: export Athena {name}: {len(aws)} linhas equivalentes.')
output=Path(a.pasta)/'reconciliacao_aws.txt';output.write_text('\n'.join(logs),encoding='utf-8');print('\n'.join(logs))
