"""Pipeline Spark Bronze -> Silver -> Gold. AWS Glue 5.1 (ou 5.0, se disponível no Lab) / Spark 3.5.
Testado localmente em Spark 3.5.6; integração IAM/S3/Catálogo exige execução no Lab.
Parâmetros AWS: JOB_NAME, CONFIG_S3_PATH, INPUT_PREFIX, OUTPUT_PREFIX, RUN_ID, DATABASE.
Cada RUN_ID é um snapshot completo das 3 edições; sobrescrita só dentro desse snapshot.
"""
import json,sys,functools
from pyspark.sql import functions as F
from pyspark.sql import types as T

def silver_one(spark,path,e,cfg):
    raw=(spark.read.option('header',True).option('inferSchema',False)
         .option('multiLine',True).option('quote','"').option('escape','"')
         .option('mode','FAILFAST').csv(path))
    original=list(raw.columns); n=raw.count()
    mp=cfg['mapeamento'][e]
    missing=set(mp.values())-set(original)
    if missing:raise ValueError(f'Colunas ausentes em {e}: {missing}')
    # Renomear todas as colunas elimina ambiguidade de pontos, barras e tuplas no cabeçalho.
    raw=raw.toDF(*[f'c{i}' for i in range(len(original))])
    dedup=raw.dropDuplicates().cache(); nd=dedup.count()
    cols=[]
    for dest,source in mp.items():
        c=F.trim(F.col(f'c{original.index(source)}'))
        cols.append(F.when(c!='',c).alias(dest))
    x=dedup.select(*cols)
    if x.filter(F.col('id_resposta').isNull()).limit(1).count():raise ValueError('ID nulo')
    if x.groupBy('id_resposta').count().filter('count > 1').limit(1).count():
        raise ValueError('IDs conflitantes após remover duplicatas exatas; investigar sem escolher arbitrariamente')
    for c in cfg['binary']:
        v=F.lower(F.col(c))
        if x.filter(v.isNotNull() & ~v.isin('1','0','true','false','sim','não','nao','prefiro não informar')).limit(1).count():
            raise ValueError(f'Domínio binário inválido: {e}/{c}')
        x=x.withColumn(c,F.when(v.isin('1','true','sim'),1).when(v.isin('0','false','não','nao'),0))
    x=x.withColumn('idade',F.col('idade').cast('double'))
    x=x.withColumn('idade_invalida',F.col('idade').isNotNull() & ~F.col('idade').between(14,100))
    x=x.withColumn('idade',F.when(~F.col('idade_invalida'),F.col('idade')))
    x=x.withColumn('faixa_salarial_original',F.col('faixa_salarial'))
    x=x.withColumn('salario_anomalo',F.col('faixa_salarial').isNotNull() & ~F.col('faixa_salarial').isin(cfg['salarios']))
    x=x.withColumn('faixa_salarial',F.when(~F.col('salario_anomalo'),F.col('faixa_salarial')))
    x=x.withColumn('salario_alto',F.when(F.col('faixa_salarial').isNotNull(),F.when(F.col('faixa_salarial').isin(cfg['salarios'][7:]),1).otherwise(0)))
    opts=['ia_gratuita','ia_paga_pessoa','ia_paga_empresa','ia_copilot']
    use=functools.reduce(lambda a,b:a|b,[F.coalesce(F.col(c)==1,F.lit(False)) for c in opts])
    known=functools.reduce(lambda a,b:a|b,[F.col(c).isNotNull() for c in opts+['ia_nao_usa']])
    conflict=use & F.coalesce(F.col('ia_nao_usa')==1,F.lit(False))
    x=x.withColumn('ia_resposta_conflitante',conflict)
    x=x.withColumn('ia_usa',F.when(known & ~conflict,use.cast('int')))
    if 'ia_resultado' not in x.columns:x=x.withColumn('ia_resultado',F.lit(None).cast('string'))
    x=x.withColumn('respondente_chave',F.sha2(F.concat(F.lit(e+'|'),F.col('id_resposta')),256)).drop('id_resposta')
    x=x.withColumn('edicao_pesquisa',F.lit(e)).withColumn('arquivo_origem',F.lit(cfg['fontes'][e])).cache()
    quality={'edicao':e,'linhas_csv':n,'colunas_csv':len(original),'duplicatas_exatas':n-nd,'linhas_silver':x.count(),
      'residentes_brasil':x.filter('vive_no_brasil = 1').count(),'salarios_anomalos':x.filter('salario_anomalo').count(),
      'ia_conflitante':x.filter('ia_resposta_conflitante').count(),'idades_invalidas':x.filter('idade_invalida').count()}
    assert n>0 and quality['linhas_silver']==n-quality['duplicatas_exatas']
    dedup.unpersist()
    return x,quality

def gold_tables(s,cfg):
    b=s.filter('vive_no_brasil = 1')
    # Explode vetores de structs evita varrer a Silver uma vez por indicador.
    ds=[F.struct(F.lit(c).alias('dimensao'),F.col(c).cast('string').alias('categoria')) for c in cfg['dims']]
    l=b.select('edicao_pesquisa',F.explode(F.array(*ds)).alias('v')).select('edicao_pesquisa','v.*').filter('categoria is not null')
    counts=l.groupBy('edicao_pesquisa','dimensao','categoria').agg(F.count('*').alias('n'))
    den=counts.groupBy('edicao_pesquisa','dimensao').agg(F.sum('n').alias('denominador'))
    dist=counts.join(den,['edicao_pesquisa','dimensao']).withColumn('percentual',100*F.col('n')/F.col('denominador'))
    ms=[F.struct(F.lit(c).alias('indicador'),F.col(c).cast('int').alias('valor')) for c in cfg['metrics']]
    l=b.select('edicao_pesquisa',F.explode(F.array(*ms)).alias('v')).select('edicao_pesquisa','v.*')
    rates=l.groupBy('edicao_pesquisa','indicador').agg(F.coalesce(F.sum('valor'),F.lit(0)).alias('n'),F.count('valor').alias('denominador'))
    rates=rates.withColumn('percentual',F.when(F.col('denominador')>0,100*F.col('n')/F.col('denominador')))
    ps=[F.struct(F.lit(c).alias('dimensao'),F.col(c).alias('categoria')) for c in ['cargo','senioridade','regiao','modelo_atual','genero','setor']]
    l=b.select('edicao_pesquisa','salario_alto',F.explode(F.array(*ps)).alias('v')).select('edicao_pesquisa','salario_alto','v.*').filter('categoria is not null and salario_alto is not null')
    pay=l.groupBy('edicao_pesquisa','dimensao','categoria').agg(F.sum('salario_alto').alias('n_salario_alto'),F.count('*').alias('denominador'))
    pay=pay.withColumn('percentual',100*F.col('n_salario_alto')/F.col('denominador'))
    return {'distribuicoes':dist,'indicadores':rates,'salarios_segmentos':pay}

def catalog_table(client,db,name,df,location,partitioned=False):
    fields=[{'Name':f.name,'Type':f.dataType.simpleString()} for f in df.schema.fields if not (partitioned and f.name=='edicao_pesquisa')]
    sd={'Columns':fields,'Location':location.rstrip('/')+'/',
        'InputFormat':'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
        'OutputFormat':'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
        'SerdeInfo':{'SerializationLibrary':'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe','Parameters':{'serialization.format':'1'}}}
    table={'Name':name,'TableType':'EXTERNAL_TABLE','Parameters':{'classification':'parquet','EXTERNAL':'TRUE'},'StorageDescriptor':sd,
        'PartitionKeys':[{'Name':'edicao_pesquisa','Type':'string'}] if partitioned else []}
    try:client.create_table(DatabaseName=db,TableInput=table)
    except client.exceptions.AlreadyExistsException:client.update_table(DatabaseName=db,TableInput=table)
    if partitioned:
        for e in ['2023','2024','2025-2026']:
            psd=dict(sd,Location=location.rstrip('/')+'/edicao_pesquisa='+e+'/')
            part={'Values':[e],'StorageDescriptor':psd}
            try:client.create_partition(DatabaseName=db,TableName=name,PartitionInput=part)
            except client.exceptions.AlreadyExistsException:client.update_partition(DatabaseName=db,TableName=name,PartitionValueList=[e],PartitionInput=part)

def main():
    import boto3
    from awsglue.utils import getResolvedOptions
    from awsglue.context import GlueContext
    from awsglue.job import Job
    from pyspark.context import SparkContext
    args=getResolvedOptions(sys.argv,['JOB_NAME','CONFIG_S3_PATH','INPUT_PREFIX','OUTPUT_PREFIX','RUN_ID','DATABASE'])
    gc=GlueContext(SparkContext.getOrCreate());spark=gc.spark_session
    spark.conf.set('spark.sql.shuffle.partitions','8')
    job=Job(gc);job.init(args['JOB_NAME'],args)
    inp=args['INPUT_PREFIX'].rstrip('/');out=args['OUTPUT_PREFIX'].rstrip('/')
    if not inp.startswith('s3://') or not out.startswith('s3://'):raise ValueError('Usar prefixos s3://')
    if out==inp or out.startswith(inp+'/') or inp.startswith(out+'/'):raise ValueError('Separar prefixos de entrada e saída')
    if len(out[5:].split('/'))<2:raise ValueError('Nunca usar a raiz do bucket como saída')
    import re
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args['RUN_ID']):raise ValueError('RUN_ID: apenas letras, números, _ e -')
    cp=args['CONFIG_S3_PATH'][5:].split('/',1)
    cfg=json.loads(boto3.client('s3').get_object(Bucket=cp[0],Key=cp[1])['Body'].read())
    root=out+'/execucao='+args['RUN_ID'];frames=[];dq=[]
    for e in cfg['fontes']:
        x,q=silver_one(spark,inp+'/'+cfg['fontes'][e],e,cfg);frames.append(x);dq.append(q);print('QUALIDADE',json.dumps(q))
    s=functools.reduce(lambda a,b:a.unionByName(b),frames).cache()
    assert s.count()==sum(q['linhas_silver'] for q in dq)
    # Sobrescrita do snapshot dedicado, nunca Bronze nem conversões anteriores.
    s.write.mode('overwrite').option('compression','snappy').partitionBy('edicao_pesquisa').parquet(root+'/silver/profissionais')
    tables=gold_tables(s,cfg);tables['qualidade']=spark.createDataFrame(dq)
    client=boto3.client('glue');db=args['DATABASE']
    try:client.create_database(DatabaseInput={'Name':db})
    except client.exceptions.AlreadyExistsException:pass
    catalog_table(client,db,'silver_profissionais',s,root+'/silver/profissionais',True)
    for name,df in tables.items():
        location=root+'/gold/'+name
        df.coalesce(1).write.mode('overwrite').option('compression','snappy').parquet(location)
        catalog_table(client,db,'gold_'+name,df,location)
    for q in dq:
        e=q['edicao'];back=spark.read.parquet(root+'/silver/profissionais/edicao_pesquisa='+e).count()
        assert back==q['linhas_silver'],f'Reconciliação falhou: {e}'
    print('SUCESSO: snapshot e catálogo atualizados',root)
    job.commit()
if __name__=='__main__':main()
