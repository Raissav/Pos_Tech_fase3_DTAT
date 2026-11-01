"""Teste de paridade Spark versus tabelas Pandas calculadas dos mesmos arquivos."""
import json,sys,tempfile
from pathlib import Path
import pandas as pd
from pyspark.sql import SparkSession
from glue_job import silver_one,gold_tables
base=Path(__file__).parent;cfg=json.load(open(base/'config_pipeline.json'))
spark=SparkSession.builder.master('local[2]').appName('validacao-tech-challenge').config('spark.sql.shuffle.partitions','2').config('spark.driver.memory','2g').getOrCreate()
spark.sparkContext.setLogLevel('ERROR')
frames=[];qs=[]
for e,f in cfg['fontes'].items():
 x,q=silver_one(spark,str(Path(sys.argv[1]).resolve()/f),e,cfg);frames.append(x);qs.append(q);print(q,flush=True)
s=frames[0]
for x in frames[1:]:s=s.unionByName(x)
s=s.cache()
expected=Path(sys.argv[2]);checks=[]
for name,df in gold_tables(s,cfg).items():
 a=df.toPandas();b=pd.read_csv(expected/(name+'.csv'),dtype={'edicao_pesquisa':str})
 keys=['edicao_pesquisa','indicador'] if name=='indicadores' else ['edicao_pesquisa','dimensao','categoria']
 a=a.sort_values(keys).reset_index(drop=True);b=b.sort_values(keys).reset_index(drop=True)
 a=a[b.columns]
 pd.testing.assert_frame_equal(a,b,check_dtype=False,check_exact=False,atol=1e-9,rtol=1e-9)
 checks.append(f'PASS: {name}: {len(a)} linhas; todas as categorias, contagens e percentuais equivalentes.')
q=pd.DataFrame(qs);b=pd.read_csv(expected/'qualidade.csv',dtype={'edicao':str});q=q[b.columns]
pd.testing.assert_frame_equal(q,b,check_dtype=False)
checks.append('PASS: relatório de qualidade equivalente; leitura Spark preservou linhas e campos mapeados.')
parquet_test=Path(tempfile.mkdtemp(prefix='spark_test_'))/'silver'
s.write.mode('overwrite').option('compression','snappy').partitionBy('edicao_pesquisa').parquet(str(parquet_test))
assert spark.read.parquet(str(parquet_test)).count()==14002
checks.append('PASS: escrita e releitura Parquet Spark: 14.002 registros.')
(expected/'validacao_spark.txt').write_text('\n'.join(checks)+'\n\nSpark '+spark.version+'; execução local, não AWS.\n',encoding='utf-8')
print('\n'.join(checks));spark.stop()
