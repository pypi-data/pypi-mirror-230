__author__ =     "CARLOS PIVETA"
__collaborators__ = "CARLOS PIVETA, LEONARDO BOTELHO"
__license__ =    "DADOS"
__version__ =    "1.1.8"
__maintainer__ = "CARLOS PIVETA"
__status__ =     "Production"

import os
import re
import sys
import glob
import time
import shutil
import zipfile
import logging
import warnings
import holidays
import pandas as pd
from tqdm import tqdm
from unidecode import unidecode
from pyspark import HiveContext
from impala.dbapi import connect
from impala.util import as_pandas
from pyspark.sql import SQLContext
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit
from datetime import date,datetime,timedelta
from pyspark.sql import Row, functions as spf
from dateutil.relativedelta import relativedelta
from pyspark.sql.types import IntegerType, StringType, StructType, StructField
warnings.filterwarnings("ignore")

# -------------------------------------------------------------------------------------------------------------------------------
# | CLASS CONN
# -------------------------------------------------------------------------------------------------------------------------------
class conn():   
    
    def __init__(self,strEnv = None,strUser= None,strpassword= None,strSandbox = None):
        
        #AJUSTE DE USUARIO
        try:
            self.user  = os.environ['HADOOP_USER_NAME']
        except:
            self.user  = 'SEM USUARIO'
        
        if strEnv == None:
            self.environment = 'DEV'
        else:
            self.environment = strEnv.upper()
        
        if strUser != None:
            self.sandbox = strSandbox
            self.user = strUser
            self.pswd = strpassword
        else:
            if self.user  != 'SEM USUARIO':
                try:
                    self.sandbox = os.environ['WORKLOAD_SANDBOX']
                    self.pswd = os.environ['WORKLOAD_PASSWORD']
                    self.environment = 'DEV'                        
                except Exception as e:
                    self.sandbox = None
                    self.pswd = None
                    self.environment = 'DEV'
                    print('Criar variaveis de ambiente !!!!')
                    print(f'https://ml-afd78f89-d96.cloudera.lg50-5lsa.cloudera.site/{s.user}/settings/environment')
                    print("""

                    1) Preencher a sua senha da cloudera no 
                        WORKLOAD_PASSWORD [senhaSuperSecreta]

                        caso não lembre a sua senha, será necessario reiniciar ela:
                        https://console.altus.cloudera.com/iam/index.html#/my-account

                    2)  Criar as variaveis de ambiente a baixo:
                        WORKLOAD_SANDBOX       sandbox_NomeDoSeuSandbox
                        WORKLOAD_ENVIRONMENT   dev
                    """)
            else:
                self.sandbox = None
                self.pswd = None
                self.environment = 'PROD'
        
        #AJUSTE DE SERVIDOR
        try:
            self.hostImpala = os.environ['IMPALA']
            self.hostImpala = os.environ['IMPALA_PORTA']
        except:
            self.hostImpala = 'coordinator-impala-users-prod-1.env-8gtbx9.dw.lg50-5lsa.cloudera.site'
            self.portImpala = '443'
        try:
            self.hostHive = os.environ['HIVE']
        except:
            self.hostHive = 'hs2-hive-users-1.env-8gtbx9.dw.lg50-5lsa.cloudera.site'
        
            
            
            
        strPasta="./";
        strfile = '/app/mount/'+strPasta;
        self.qtEtapas = 0;
        
        if os.path.exists(strfile):
            path = strfile;
        else:
            path = strPasta;
        try:
            with open(path+"CONTROLE.txt", 'r') as f:
                self.dbControle = f.readline().strip();
        except:
            self.dbControle = self.sandbox;
                
        #conexções
        self.spark = None
        self.impala = None
        self.hive = None
        self.tpConn = None
        
    def getSpark(self,dPrint = True, dist = False):
        """
        spark = s.getSpark([dPrint = False])
        Função de conexão para consulta/execução de comandos SQL via Spark        
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        if dist == True:
            spark = SparkSession\
                .builder\
                .appName("pySpark_dist")\
                .config("spark.hadoop.yarn.resourcemanager.principal", self.user)\
                .config("spark.yarn.access.hadoopFileSystems","s3a://cloudera-cdp-prod")\
                .config("spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation","true")\
                .config("hive.exec.dynamic.partition.mode","nonstrict")\
                .config("spark.sql.shuffle.partitions","50")\
                .config("spark.driver.memory","4g")\
                .config("spark.executor.memory","24g")\
                .config("spark.executor.cores","4")\
                .config("spark.executor.instances","4")\
                .config("spark.driver.cores","2")\
                .getOrCreate()
            self.spark = spark
            self.tpConn = spark
            return self.spark
        elif (self.spark == None and self.environment == 'PROD'):
            spark = SparkSession \
                .builder \
                .appName("pySpark_prod") \
                .config("hive.exec.dynamic.partition.mode", "nonstrict") \
                .config("spark.yarn.access.hadoopFileSystems", "s3a://cloudera-cdp-prod") \
                .config("spark.sql.autoBroadcastJoinThreshold", "-1") \
                .config("spark.sql.shuffle.partitions", "50") \
                .config("spark.sql.legacy.allowCreatingManagedTableUsingNonemptyLocation", "true") \
                .enableHiveSupport() \
                .getOrCreate()
            self.spark = spark
            self.tpConn = spark
            return self.spark
        elif self.spark == None:
            try:
                spark = SparkSession \
                    .builder \
                    .appName('pySpark_dev') \
                    .master("local[*]") \
                    .config("spark.hadoop.yarn.resourcemanager.principal", self.user) \
                    .config("spark.sql.hive.hiveserver2.jdbc.url",
                    "jdbc:hive2://"+self.hostHive+"/default;transportMode=http;httpPath=cliservice;ssl=true;retries=3;user={0};password={1}".format(
                    self.user, self.pswd)) \
                    .config("spark.datasource.hive.warehouse.read.via.llap", "false") \
                    .config("spark.datasource.hive.warehouse.read.jdbc.mode", "client") \
                    .config("spark.datasource.hive.warehouse.metastoreUri",
                    "thrift://datalake-prod-master0.cloudera.lg50-5lsa.cloudera.site:9083,\
                    thrift://datalake-prod-master1.cloudera.lg50-5lsa.cloudera.site:9083") \
                    .config("spark.datasource.hive.warehouse.load.staging.dir",
                    "s3a://cloudera-cdp-prod/storage/"+self.sandbox+"/staging") \
                    .getOrCreate()
                self.spark = spark
                self.tpConn = spark
                if dPrint == True : print("Sessão do Spark Criada !") 
                return spark
            except Exception as e:
                spark = SparkSession.builder.getOrCreate()
                self.spark = spark
                self.tpConn = spark
                return self.spark
        else:
            self.tpConn = self.spark
            return self.spark
                
    def getHive(self,dPrint = True):
        """
        spark = s.getSpark([dPrint = False])
        Função de conexão para consulta/execução de comandos SQL via Spark
        
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a mensagem de retorno

        Argumentos:
        -----------
        self: objeto
            Objeto que chama a função.
        dPrint : bool (opcional)
            Define se a mensagem de retorno será impressa.
        dist : bool (opcional)
            Define se a sessão será distribuída ou local.

        Retorna:
        --------
        spark : objeto
            Sessão do Spark.
        """
        if self.hive == None:
            if self.spark == None:
                self.getSpark()
                
            try:
                from pyspark_llap import HiveWarehouseSession
                hive = HiveWarehouseSession.session(self.spark).build()
                self.hive = hive
                self.tpConn = hive
                if dPrint == True : print("Sessão do Hive Criada !") 
                return self.hive
            except Exception as e:
                if self.environment == 'DEV':
                    if dPrint == True : print("ERRO! ao criar a sessão do Hive : Mudar versão do Spark para Spark 2.4.7 - CDP 7.2.11 - CDE 1.13 - HOTFIX-2")
                return None
        else:
            self.tpConn = self.hive
            return self.hive
            
    def getImpala(self,dPrint = True):
        """
        impala = sc.getImpala([dPrint = False])
        Função de conexão para consulta/execução de comandos SQL via Impala        
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        try:
            impala_conn = connect(host=self.hostImpala,
                           port=self.portImpala,
                           auth_mechanism='LDAP',
                           user=self.user,
                           password=self.pswd,
                           use_http_transport=True,
                           http_path='/cliservice',
                           use_ssl=True)
            impala_cur = impala_conn.cursor()
            self.impala = impala_cur
            self.tpConn = impala_cur
            if dPrint == True : print("Sessão do Impala Criada !")
            return impala_cur
        except Exception as e:
            if dPrint == True : print("ERRO! ao criar a sessão do Impala !")
            if dPrint == True : print(e)
            if dPrint == True : print("""
Você esta com problema com sua senha !!!!
            """)
            if dPrint == True : print('confirgure novamente sua senha do Machine Learning !!!!')
            if dPrint == True : print(f'https://ml-afd78f89-d96.cloudera.lg50-5lsa.cloudera.site/{self.user}/settings/environment')
            if dPrint == True : print("""
1) Preencher a sua senha da cloudera no 
    WORKLOAD_PASSWORD [senhaSuperSecreta]

    caso não lembre a sua senha, será necessario reiniciar ela:
    https://console.altus.cloudera.com/iam/index.html#/my-account

2) parar e subir uma nova seção desse projeto
                """)
                    
    def getConn(self,dPrint = True):
        """
        tpConn = sc.getConn([dPrint =False])
        Função que retorna a melhor conexão com base no ambiente que está sendo rodado     
        Parameters
        ----------
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        if self.tpConn == None or self.impala !=None:
            if self.environment.upper() == 'DEV':
                self.getHive(dPrint)
                self.tpConn = self.hive
            else:
                self.getHive(dPrint)
                self.tpConn = self.spark
        return self.tpConn
    
    def dropSandbox(self, strTable,dPrint = True):
        """
        dropSandbox(strTable = 'tabela',[dPrint =True])
        Função para apagar uma tabela do sandbox
        Parameters
        ----------
        strTable : str
            Nome da tabela a ser deletada do ambiente sandbox
        dPrint : bool (optional)
            Define se será impresso a menssagem de retorno
            
        """
        if self.impala != None:
            try:
                self.impala.execute("drop table "+self.sandbox+"."+strTable+" PURGE")
                if dPrint == True :print("A tabela {} deletada do sandbox {}".format(strTable,self.sandbox))
            except Exception as e:
                if dPrint == True: print("A tabela {} não existe no sandbox {}".format(strTable,self.sandbox))
                if dPrint == True: print(e)
        elif self.spark == None:
            self.getSpark(dPrint)
            try:
                self.spark.sql("drop table "+self.sandbox+"."+strTable+" PURGE")
                if dPrint == True :print("A tabela {} deletada do sandbox {}".format(strTable,self.sandbox))
            except Exception as e:
                if dPrint == True: print("A tabela {} não existe no sandbox {}".format(strTable,self.sandbox))
                if dPrint == True: print(e)
    
    def execute(self,query,df = False):
        if self.impala == None:
            self.getImpala(dPrint = False)
        try:
            self.impala.execute(query)
            print('Comando Executado com sucesso')
            if df == True:
                table = None
                vet = query.replace('\n',' ').split(' ')
                for p in range(len(vet)):
                    if vet[p].upper() == 'TABLE':
                        table = vet[p+1]
                        print(table,vet[p],vet[p+1])
                if table != None:
                    vet2 = table.split('.')
                    schema = vet2[0]
                    tabela = vet2[1]
                    return self.readTable(schema,tabela)
        except Exception as e:
            print('ERRO! Comando NÃO executado !!!')
            print(e)
            
    def execImpala(self,strQuery = 'select'):
        """
        execImpala(strQuery = 'select * from table')
        Função para executar um comando sql e devolver em formato dataframe pandas

        Parameters
        ----------
        strQuery : str
            stgring com o comando sql a ser executado
        
        Returns
        ------- 
        dataframe
            dataframe com o retorno da string sql executada
        """
        try:
            self.getImpala(dPrint = False)
            impala = self.impala
            impala.execute(strQuery)
            df = as_pandas(impala)
            return df
        except Exception as e:
            print('ERRO!!! ')
            print(e) 
            
    def getLastPartition(self,strSchema,strTable,exportDataframe = False,intLimit = None,dPrint = True):
        """
        [dtPartition] = getLastPartition(strSchema = 'abc',strTable ='tabela',[exportDataframe = True], [intLimit = 1000],dPrint = True)
        Função para pegar a ultima partição caso exista 
        Parameters
        ----------
        strSchema: str
            Nome do database aonde a tabela esta localizada
        strTable : str
            Nome da tabela a ser deletada do ambiente sandbox
        exportDataframe: bol
            marcação [True/False] se o retorno será em dataframe ou string
        intLimit: int
            limitação de linhas de retorno
        dPrint: bol
            Define se será impresso a menssagem de retorno
            
        
        Returns
        -------
        (exportDataframe = False) str
            valor da ultima partição da tabela
        
        (exportDataframe = True) dataframe
            dataframe com as informações da ultima partição
            
        """
        
        if self.tpConn == None or self.impala != None:
            self.getConn()
            
        strLimit  = '' if intLimit == None else ' limit '+str(intLimit)
        try:
            partition = self.tpConn.sql("SHOW PARTITIONS {}.{}".format(strSchema,strTable)).agg({"partition": "max"}).collect()[0][0].split('/')[0].split('=')
            if exportDataframe == False:
                    if dPrint == True: print('ultima partição {} = {}'.format(partition[0],partition[1]))
                    return partition[1]
            else:
                try:
                    if dPrint == True: print('ultima partição {} = {}'.format(partition[0],partition[1]))
                    strsql = "select * from {}.{} where {}='{}' {}".format(strSchema,strTable,str(partition[0]),str(partition[1]),strLimit)
                    df = self.tpConn.sql(strsql)
                    return df
                except Exception as e:
                    df = self.tpConn.sql('select * from {}.{} {}'.format(strSchema,strTable,strLimit))
                    return df
        except Exception as e:
            if dPrint == True: print('Tabela {} não possui partição'.format(strTable))
            print(e)
    def getMaxPartitionTable(self,strSchema=None,strTable="",strPartition="dt_ingest"):
        """
        [dtPartition] = getMaxPartitionTable(strSchema = 'abc',strTable ='tabela',strPartition='dt_ingest')
        Função para pegar a maior partição
        Parameters
        ----------
        strSchema: str
            Nome do database aonde a tabela esta localizada
        strTable : str
            Nome da tabela a ser deletada do ambiente sandbox
        strPartition : str
            Nome da partição
        Returns Valor da partição com maior valor    
        """;
        if((strSchema is None)|(strSchema=="")):
            strTableName = strTable if(len(strTable.split("."))>1) else strTable;
        else:
            strTableName = strSchema+"."+strTable.split(".")[1] if(len(strTable.split("."))>1) else strSchema +"."+ strTable;
        strNmPartition = strPartition.upper();
        dfListPartition = self.tpConn.sql("SHOW PARTITIONS {0}".format(strTableName));
        vMaxPartition = dfListPartition \
        .withColumn("posPartition",spf.expr(f"instr(upper(partition),'{strNmPartition}')+length('{strNmPartition}')+1")) \
        .withColumn("vStr",spf.expr(f"substring(partition,posPartition)")) \
        .withColumn("findP",spf.expr(f"ifnull(nullif(instr(vStr,'/')-1,-1),length(vStr))")) \
        .withColumn("valuePartition",spf.expr(f"substring(vStr,1,findP)")) \
        .agg({"valuePartition": "max"}).collect()[0][0];
        return vMaxPartition;
    
    def toSandBox(self,strSchema,strTable,ultimaParticao = False,intLimit = None,CampoDocumento = None,tpDocumento = None):
        """
        toSandBox(strSchema = 'abc',strTable = 'tabela',[ultimaParticao = False],[intLimit = 100],[CampoDocumento = None],[tpDocumento = None])
        Função para salvar uma tabela do ambiente produtivo no ambiente sandbox com id unico caso seja necessário
        Parameters
        ----------
        strTable : str
            Nome da tabela a ser criada do ambiente sandbox
        ultimaParticao bol (optional)
            marcação [True/False] se o retorno será apenas da ultima partição [True], ou total [False]
        intLimit: int
            limitação de linhas de retorno
        CampoDocumento str(optional)
            Nome do campo com informação do numero de documento (cpf ou cnpj) para trazer as informações do id unico
        tpDocumento
            tipo do documento [Raiz ou Completo] a ser cruzado com a tabela pessoa.pessoa
        
        """
        if self.impala == None:
            if self.tpConn == None:
                self.getConn()
            
        self.dropSandbox(strTable) 
        
        strLimit  = '' if intLimit == None else ' limit '+str(intLimit)
        
        try:
            if CampoDocumento == None:
                if ultimaParticao == False:
                    if self.impala == None:
                        self.spark.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                             AS SELECT * FROM {}.{} {}".format(self.sandbox,strTable,strSchema,strTable,strLimit))
                    else:
                        self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                             AS SELECT * FROM {}.{} {}".format(self.sandbox,strTable,strSchema,strTable,strLimit))
                else:
                    strPartition = self.getLastPartition(strSchema,strTable)
                    if self.impala == None:
                        self.spark.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                                   AS SELECT * FROM {}.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,strPartition,strLimit))
                    else:
                        self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                                                   AS SELECT * FROM {}.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,strPartition,strLimit)) 
            else:        
                if tpDocumento != None and tpDocumento.upper() == 'RAIZ':
                    strCampoPessoa = 'num_raiz_doc_pes'
                else:
                    strCampoPessoa = 'num_doc_pes'
                    if ultimaParticao == False:
                        if self.impala == None:
                            self.tpConn.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strLimit))
                        else:
                            self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strLimit))
                    else:
                        strPartition = self.getLastPartition(strSchema,strTable)
                        if self.impala == None:
                            self.tpConn.executeUpdate("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strPartition,strLimit))
                        else:
                            self.impala.execute("CREATE EXTERNAL TABLE {}.{} TBLPROPERTIES('parquet.compression'='SNAPPY', 'external.table.purge'='true') \
                            AS SELECT b.id_pes ,a.* FROM {}.{} a LEFT JOIN PESSOA.PESSOA b ON a.{} = b.{} where dt_ingest = '{}' {}".format(self.sandbox,strTable,strSchema,strTable,CampoDocumento,strCampoPessoa,strPartition,strLimit))
                    
            print('Tabela {}.{} salva !'.format(self.sandbox,strTable))
            print('')
        except Exception as e:
            print('ERRO! Tabela {}.{} NÃO salva !'.format(self.sandbox,strTable))
            print(e)
            
    def readTable(self,strSchema ,strTable, bolSandbox = False):
        """
        readTable(strSchema = abc ,strTable = tabela, [bolSandbox = False])
        Função para carregar uma tabela (sandbox ou corporativo) em um dataframe
        Parameters
        ----------
        strSchema: str
            Nome do database aonde a tabela esta localizada
        strTable : str
            Nome da tabela a ser carregada
        bolSandbox bol (optional)
            marcação [True/False] se o retorno a base do ambiente produtivo [False] ou do Sandbox ['True']
        """
        
        if strSchema[:7].upper() == 'SANDBOX':
            bolSandbox = True
        
        if bolSandbox == True:
            self.getSpark()
        else:
            self.getConn()
            
        flagSandbox = True if self.environment != 'DEV' else bolSandbox
        schema = self.sandbox if flagSandbox == True else strSchema
        query = schema+'.'+strTable
        
        conx = self.spark if [self.environment != 'DEV' or flagSandbox == True] else self.hive
        print(conx)
        try:
            df = conx.table(query)
            print('Tabela {} carragada !'.format(query))
        except Exception as e:
            df = None
            print('ERRO! Tabela {} NÃO carragada !'.format(query))
            print(e)
            
        return df
        
        print(flagSandbox,schema)
        
        
    def execute(self,strQuery):
        self.getConn()
        conx = self.spark if [self.environment != 'DEV'] else self.hive
        try:
            df = conx.sql(strQuery)
            print('querry {} executada !'.format(strQuery))
        except Exception as e:
            df = None
            print('ERRO! querry {} NÃO executada !'.format(strQuery))
            print(e)
            
        return df
   
    def getResult(self,query):
        """
        val = getResult(query = 'select max(valor) from tabela')
        Função para trazer para uma variavel o valor de resultado de uma query
        
        Parameters
        ----------
        query : str
            query a ser execultada
        """
        self.getConn()
        try:
            return self.tpConn.sql(query).collect()[0][0]
        except Exception as e:
            print('ERRO! A query informada não retornou!')
            print(e)
            
    def saveSandbox(self,df,strTableName,bolReturn = False):
        """ 
        saveSandbox(df = DFA,strTableName = 'nome da tabela')
        Função salvar dataframe como tabela no sandbox
        
        Parameters
        ----------
        df 
            Dataframe que deseja salvar no sandbox.
            
        strTableName : str
            Nome da tabela que deseja salvar no sandbox.
        Boolean
            marcação de [True, False] se a chamada vai retornar o sucesso ou não.
            
        Returns
        ------- 
        Boolean
            flag com marcação se a carga deu certo ou não
        
        """
        ret = True
        try:
            df = self.spark.createDataFrame(df)
        except Exception as e:
            print(e)
            pass
        
        self.dropSandbox(strTableName)
        
        try:
            df.write.format('parquet').mode('overwrite').saveAsTable('{}.{}'.format(self.sandbox,strTableName))
            print('Tabela {} salva no sandbox {} !'.format(strTableName,self.sandbox))
        except Exception as e:
            print('ERRO! Tabela {} NÃO salva no sandbox {} !'.format(strTableName,self.sandbox))
            print(e)
            ret = False
        if bolReturn == True:
            return ret
            
    def setTmpView(self,df,name):
        """ 
        DFA = setTmpView(df = DFA)
        Função para criar uma tempview a partir de um dataframe
        
        Parameters
        ----------
        df 
            Dataframe que deseja transformar em tabela temporaria
        name : str
            Nome da tabela temporaria a ser criada.
            
        """
        try:
            df.createOrReplaceTempView(f"{name}")       
        except Exception as e:
            print('ERRO! Não foi possivel criar a Temp View {}'.foramt(name))
            print(e)
    def setColumnsUp(self,df):
        """ 
        DFA = setColumnsUp(df = DFA)
        Função para transformar o nome de todas as tabelas de um dataframe Spark em Maiúscula
        
        Parameters
        ----------
        df 
            Dataframe que deseja transformar o nome das colunas para Maiúscula
            
        """ 
        df=df.select([spf.col(x).alias(x.upper()) for x in df.columns])
        return df
    
    def setColumnsLow(self,df):
        """ 
        DFA = setColumnsLow(df = DFA)
        Função para transformar o nome de todas as tabelas de um dataframe Spark em Minúscula
        
        Parameters
        ----------
        df 
            Dataframe que deseja transformar o nome das colunas para Minúscula
            
        """ 
        df=df.select([spf.col(x).alias(x.upper()) for x in df.columns])
        return df
    
    def setQueryToSandbox(self,strQuery,listDbs,strAmbiente):
        """ 
        strQ = 'select * from db_crm.gg a left join db_Corporativo.aa b on a.id = b.id'
        LISTADB = ['db_crm','db_Corporativo']
        
        query = setQueryToSandbox(strQuery = strQ,listDbs = LISTADB,strAmbiente = 'DEV')
        Função para transformar a query com origem no corporativo para o sandbox
        
        Parameters
        ----------
        strQuery str
            querry a ser executada
        listDbs list
            lista de databases a serem subistituidos pelo sandbox
        strAmbiente str
            embiente no qual está sendo executada
        
        """ 
        if strAmbiente.upper() == 'DEV':
            for tCol in listDbs:
                try:
                    strQuery = strQuery.replace(tCol,self.sandbox).replace('sbx_','')
                except Exception as e:
                    print(e)
                    pass
        return strQuery;
    
    def sendToCsv(self,df,tpDf = 'SPARK',caminhoArquivo = None,nomeArquivo = None):
        """
        sc.sendToCsv(df = df_query,tpDf = 'SPARK',caminhoArquivo = "/home/cdsw/configs/CDO/MODELO/prod/Export/",nomeArquivo = "testeSpark")
        OR
        sc.sendToCsv(df = dfPandas,tpDf = 'Pandas',caminhoArquivo = "/home/cdsw/configs/CDO/MODELO/prod/Export/",nomeArquivo = "testePandas")
        
        Função para salvar dataframe em csv
        
        Parameters
        ----------
        df dataframe
            dataframe o qual será salvo em csv
        tpDf str
            tipo do datraframe a ser salvo [PANDAS/SPARK]
        caminhoArquivo str
            caminho onde será armazenado o csv
        nomeArquivo str
            nome do arquivo a ser salvo
        
        """
        
        if caminhoArquivo== None:
            sys.exit('Pasta não Encontrada')
            
        if caminhoArquivo[-1] != '/':
            caminhoArquivo = caminhoArquivo+'/'
        
        if not os.path.isdir(caminhoArquivo):       
            os.makedirs(caminhoArquivo)
        
        hora = str(datetime.now()+timedelta(hours=-3)).replace('-','').replace(':','').replace(' ','_')[:15]
        arquivo = "{}{}_{}.csv".format(caminhoArquivo,nomeArquivo,hora)
        try:
            if tpDf.upper() == 'SPARK':
                    df.coalesce(1).write.option('header', 'True').format('csv').save(arquivo)
            elif tpDf.upper() == 'PANDAS':
                    df.to_csv(arquivo, sep=';',index=False)
            else:
                raise ValueError("ERRO! Formato NÃO suportado !!!")
            print("csv {} salvo !!!".format(nomeArquivo))   
        except Exception as e:
            print("ERRO! csv {} NÃO salvo !!!".format(nomeArquivo))
            print(e)
    
    def replaceTbQuery(self,vQuery,vTabelas,limit_dev = 'limit 100'):
        list_tables = vTabelas.upper().split(",")
        for tb in list_tables:
            nmTb = tb.split(".")[1]
            if (self.environment == "DEV"):
                tbName = self.sandbox+"."+tb.split(".")[1];
            else:
                tbName=tb;
            vQuery = vQuery.replace(nmTb,nmTb.lower());
            vQuery = vQuery.replace(tb.lower(),tbName);  
            vQuery = vQuery.replace(tb.lower(),tbName.lower());  
            vQuery = vQuery.replace(tb,tbName);
        if(vQuery.lower().find("select")>=0):
            vQuery = vQuery+" "+limit_dev
        return vQuery;
    
    def SaveFileProces(self,DF_INSERT,vTable,vEtapa,paths3):
        """
        Função utilizada pelo time de CRM
        """
        pos = len(vTable.split("_"))-1
        contexto = vTable.split("_")[pos]
        etapa = "0"+vEtapa+"_"+contexto.upper()
        pathFile ="{0}_{1}/parquet_tmp/{2}/".format(paths3,contexto,etapa)
        DF_INSERT\
         .write\
         .format("parquet")\
         .mode("overwrite")\
         .save(pathFile)
        print(f"Arquivo salvo em: {pathFile}");
    
    def CheckPoint(self,df,table,paths3):
        pathTable = "{0}/temp/{1}/".format(paths3,table)
        self.spark.sparkContext.setCheckpointDir(pathTable)
        df = df.checkpoint()
        df.createOrReplaceTempView(table)
        return df
    
    def SetNullToString(self,df):
        """
        df2 = sc.SetNullToString(df)

        Função para alterar os valores Null para a string ''

        Parameters
        ----------
        df dataframe
            dataframe o qual será convertido

        """
        ##Converte todos os campos em String e nome das colunas tudo em CAIXA ALTA
        df = df.select([spf.when(spf.col(x).cast(StringType()).isNull(),spf.lit("")).otherwise(spf.concat(spf.lit('"'),spf.col(x), spf.lit('"')).cast(StringType())).alias(x.upper()) for x in df.columns])
        return df
    
    def SaveFileProcess(self,DF_INSERT,pathFile):
        DF_INSERT\
         .write\
         .format("parquet")\
         .mode("overwrite")\
         .save(pathFile)
        print(f"Arquivo salvo em: {pathFile}");
    
    def CheckPoint(self,df,table):
        pathTable = "{0}/temp/{1}/".format(paths3,table)
        spark.sparkContext.setCheckpointDir(pathTable)
        df = df.checkpoint()
        df.createOrReplaceTempView(table)
        return df

    def csvToSandbox(self,pasta = './arquivos/',delimiter = None,header = 'true',strEncoding= "cp1252"):
        """
        s.csvToSandbox(self,pasta = './arquivos/',delimiter = None,header = 'true' )
        
        Função para carregar arquivos de texte em um dataframe no sandbox
        
        Parameters
        ----------
        pasta str
            caminho onde está armazenado o csv
        delimiter str
            campo delimitador do csv, caso seja None ele tentará usar ';' e ','
        header str
            Marcação se o arquivo tem cabeçalho ou não (sempre em minusculo)
        
        """
        spark = self.getSpark()

        if pasta[-1] != '/':
            pasta = pasta + '/'

        if os.path.isdir(pasta) == False:
            sys.exit('Pasta não Encontrada')

        if not os.path.isdir(pasta+'carregados/'):       
            os.makedirs(pasta+'carregados/')
        
        list_of_files = []
        listFormatos = ['txt','csv']
        listFormatosM = [element.upper() for element in listFormatos]
        listFormatos = listFormatos+listFormatosM
        for t in range(len(listFormatos)):
            list_of_type = glob.glob(pasta+f'*.{listFormatos[t]}')
            list_of_files = list_of_files+list_of_type
        
        if len(list_of_files) > 0:
            for file in list_of_files:
                try:
                    arq = file.replace(pasta,'')
                    nm = unidecode(arq.replace(' ','_').replace('(','').replace(')','')).replace('-','')
                    for tp in range(len(listFormatos)):
                        nm = nm.replace(f'.{listFormatos[tp]}','')
                    
                    if delimiter == None:
                        df_Carga = spark.read.option("delimiter", ';').option("header", "true").option("encoding", strEncoding).csv(pasta+arq)
                        if len(df_Carga.columns) == 1:
                            df_Carga = spark.read.option("delimiter", ',').option("header", "true").option("encoding", strEncoding).csv(pasta+arq)
                    else:
                        df_Carga = spark.read.option("delimiter", delimiter).option("header", "true").option("encoding", strEncoding).csv(pasta+arq)
                        
                    df_Carga = self.setColumnsUp(df_Carga)
                    for i in df_Carga.columns:
                        if i[0] == '_':
                            df_Carga = df_Carga.withColumnRenamed(i, i[1:])
                            i = i[1:]
                        df_Carga = df_Carga.withColumnRenamed(i, unidecode(i))
                    
                    df_cols = df_Carga.columns

                    # INDEX DAS COLUNAS DUPLICADAS
                    duplicate_col_index = [idx for idx,
                                           val in enumerate(df_cols) if val in df_cols[:idx]]

                    # CRIANDO LISDA DAS DUPLICADAS
                    for i in duplicate_col_index:
                        df_cols[i] = df_cols[i] + '_'+ str(i)
                    
                    # RENAME
                    df_Carga = df_Carga.toDF(*df_cols)
                    df_Carga = df_Carga.select([spf.col(col).alias(re.sub("[^0-9a-zA-Z$]+","",col)) for col in df_Carga.columns])
                    move = self.saveSandbox(df_Carga,nm,True)
                    del df_Carga
                except Exception as e:
                    print('ERRO!!! Arquivo {} NÃO carregado'.format(file))
                    print(e)
                    continue
                if move == True:
                    shutil.move(file, pasta+'carregados/'+arq)
        else:
            print('Sem arquivos para serem carregados')
    
    def procImpalaSBX(self,strPasta = 'queries', strProc = 'MACRO', variaveis = {"strMes": "202302","strFim":'2023-07-31',"sandbox": "sandbox"}):
        try:    
            debugPrint = True
            path = strPasta
            files = os.listdir(strPasta)
            str_where = {}
            str_where = {**str_where, **variaveis}

            if strProc != None:
                    file = strProc
                    file = file if file[-4:].lower() == '.txt' else file+'.txt'
                    resp = filter(lambda x: x == file, files)
                    resp = list(resp)

                    if resp != []:
                        files = resp

            files = sorted(files)
            for fls in range(len(files)):
                if files[fls].endswith(".txt"):
                    arquivo = files[fls].replace('.txt','')
                    print(f'==== Rodando processo {arquivo} ====')
                    proc = files[fls].replace('.txt','')
                    with open(path+r'/'+files[fls], 'r') as file:
                        query = file.read()
                        #query = query.format(**str_where)
                        tmpTxt = query.replace(';','')
                        tmptables = re.findall(r'FROM(.*?)(\S+)',tmpTxt.upper())
                        tmptables = tmptables+re.findall(r'JOIN(.*?)(\S+)',tmpTxt.upper())
                        tmptables = tmptables+re.findall(r'JOIN(.*?)(\S+)',tmpTxt.upper())
                        tables = list(set(tmptables))
                        tmpTxt = None

                    for tt in range(len(tables)):
                        if tables[tt][1].replace('(','').replace(')','') == '':
                            pass
                        else:
                            schema = tables[tt][1].lower().split('.')[0]
                            tabela = tables[tt][1].lower().split('.')[1]
                            s.getSpark()
                            print(schema,tabela)
                            lp = s.getLastPartition(schema,tabela, dPrint=False)
                            if lp != None:
                                str_where[tables[tt][1].lower().split('.')[1]] = "" + "'" + lp +"'"

                    executionPlan = query.format(**str_where).split(';')

                    impala = s.getImpala()
                    for i in range(len(executionPlan)):
                        try:
                            val = executionPlan[i].replace('\n',' ')
                            print(f'Executando : {val}')
                            impala.execute(executionPlan[i])
                            print(f'-----FINALIZADO -----')
                        except Exception as e:
                            print(f'-----!!! ERRO !!!-----')
                            print(e)   
                            pass
        except Exception as e:
            print(e)

    def switchDB(self,vQuery,dbTo):
        newDB = dbTo;
        if(self.dbControle=="SYS_DB"):
            newDB = "SYS_" + dbTo.replace("_produtivo","").replace("_PRODUTIVO","");
        if(self.dbControle.lower()==self.sandbox):
            newDB = self.dbControle;
        vQuery = vQuery.replace(dbTo,newDB);
            
        return vQuery;
    
    def switchListTable(self,vQuery,vTabelas):
        list_tables = vTabelas.upper().split(",");
            
        for tb in list_tables:
            nmTb = tb.split(".")[1]
            dbTable=self.switchDB(tb.split(".")[0],tb.split(".")[0]);
            tbName = dbTable+"."+tb.split(".")[1];
            vQuery = vQuery.replace(tb.lower(),tbName.lower());  
            vQuery = vQuery.replace(tb,tbName);
        return vQuery;
    
    def getTimeSrv(self):
        return self.tpConn.sql("SELECT current_timestamp() - interval 3 hours as dt_processamento").collect()[0][0];

    def runProcesso(self,vArquivo):
        vDtProcessamento = datetime.strftime(self.getTimeSrv(), '%d/%m/%Y %H:%M:%S')
        S3_TIMESTAMP = vDtProcessamento
        self.qtEtapas  = self.qtEtapas+1;
        dsEtapa = f'\nEtapa {self.qtEtapas}({vArquivo}): {S3_TIMESTAMP} \n'
        print(dsEtapa)
        arquivoPy = __import__(vArquivo);

    def runPy(self,vPrint,vArquivo):
        if(vPrint==1):
            print(vArquivo);
        else:
            self.runProcesso(vArquivo);
            
    def orquestradorFiles(self,vPasta,vNmProcesso,vOrdemAvulso=0,vPrintOnly=1):
        """
        Executa todos os arquivos de 1 pasta em ordem crescente.
        Os arquivos dentro da pasta devem seguir o seguinte formato: XXX_NOME_ARQUIVO
        XXX = Deve ser numerico de 000 à 999.
        
        vPasta = Subpasta onde estão localizados os scripts .py
        vNmProcesso = Nome do Processo(necessário para execuções Avulsas, selecionar apenas alguns arquivos para execução)
        vOrdemAvulso = Valor que representa a sequência de arquivos à ser executada
        vPrintOnly = 1 (Apenas printar os arquivos do path). 0 (Executa os scrtips)
        ----------
        """
        strPasta=vPasta;
        strfile = '/app/mount/'+strPasta;
        if os.path.exists(strfile):
            path = strfile;
        else:
            path = strPasta;

        arquivosPy ="";
        print(f"\nArquivos listdir:{path} \n")
        files = os.listdir(path)
        files.sort();

        for arq in files:
            if ((arq[-3:].lower() == '.py')):
                filePy = "".join([strPasta,".",arq.replace(".py","")]);
                arquivosPy = arquivosPy+","+filePy;
                ordem = str(int(filePy.split(".")[1].split("_")[0]));
        arquivosPy = arquivosPy[1:];
        print(arquivosPy);

        dfConfigJob = self.tpConn.sql(f"""
        select arquivo
        from sandbox_crm.config_processos_crm
        where PROCESSO ='{vNmProcesso}'
        AND dt_processamento = current_date()
        """);
        dfConfigJob = dfConfigJob.dropDuplicates();
        
        listJobs = [row.arquivo for row in dfConfigJob.collect()];
        my_data =arquivosPy.split(",");
        R = Row('filename',"ordem");
        printOnly = vPrintOnly;
        print("\nJobs Avulsos:",listJobs);
        DF_FILES = self.spark.createDataFrame([R(x,int(str(x.split(".")[1].split("_")[0]))) for  x in (my_data)]);
        for arquivo in DF_FILES.sort(col("ordem")).collect():
            arquivoPy = arquivo.filename.split(".")[1];
            try:
                jobAvulso = [jobFind for i, jobFind in enumerate(listJobs) if jobFind == arquivoPy];
            except:
                jobAvulso = "";
            if((len(listJobs)>0)&(len(jobAvulso)>0)&(arquivo.ordem>=0)):
                self.runPy(printOnly,arquivo.filename);
            else:
                if((arquivo.ordem>=vOrdemAvulso)&(len(listJobs)==0)):
                    self.runPy(printOnly,arquivo.filename);
    
    def finLastFileElegiveis(self,strEtapa,strPasta,strPath):
        arquivoAnterior = "".join(["0",str(int(strEtapa)-1)])[-2:];
        
        EtapaManual = self.spark.sql(f"""
        select 
          coalesce(max(b.nu_etapa),max(a.nu_etapa),'0') as ETAPA
        from sandbox_crm.config_job_nbo  a
        left join sandbox_crm.config_job_nbo b
        on (a.dt_processamento = b.dt_processamento and b.nu_etapa < '{strEtapa}')
        where (a.dt_processamento = current_date()
        AND a.nm_arquivo not like '%NBO_ELEGIVEIS_FINAL')
        """).collect()[0][0];
        
        strfile = '/app/mount/'+strPasta;

        if os.path.exists(strfile):
            path = strfile;
        else:
            path = strPasta;

        files = os.listdir(path)
        files.sort();

        arquivosPy="";
        for arq in files:
            if ((arq[-3:].lower() == '.py')):
                filePy = "".join([strPasta,".",arq.replace(".py","")]);
                if((filePy.split(".")[1].split("_")[1].upper()=="NBO") & (filePy.split(".")[1].split("_")[2].upper()=="ELEGIVEIS") &(filePy.split(".")[1].split("_")[0]!="99")):
                    ultEtapa = str(filePy.split(".")[1].split("_")[0]);

        pathFile = "{0}/parquet_tmp/{1}/".format(strPath,ultEtapa);
        pathAnterior = "{0}/parquet_tmp/{1}/".format(strPath,arquivoAnterior);

        if(EtapaManual>=strEtapa):
            pathElegiveis = pathFile;
            print(f"\nLoad manual, arquivo da etapa {ultEtapa}!!!");
        elif(int(EtapaManual)>0):
            pathElegiveis = "{0}/parquet_tmp/{1}/".format(strPath,EtapaManual);
        else:
            pathElegiveis = pathAnterior;
        print(f"\nLoad Path:{pathElegiveis}");
        return pathElegiveis;

    def ckpLay1(self,dfCkp,pathSave,tbFile=None, tbFileWhere=None,data_ref=datetime.today().date().strftime("%Y-%m-%d")):

        # verificar se ja existe o campo COD_CRM, se nao existir precisa adicionar o UUID
        if "cod_crm" not in list(map(lambda x: x.lower(),dfCkp.columns)):
            # GERAR UUID
            unique_id_column = "unique_id_to_merge"

            all_uuids = [(str(uuid.uuid4()),) for x in range(0,dfCkp.count())]
            df_tmp_uuids = self.spark.createDataFrame(all_uuids, ['COD_CRM'])

            # monotonically_increasing_id nao esta gerando ids consecutivos.
            df_tmp_uuids = df_tmp_uuids.withColumn(unique_id_column, F.monotonically_increasing_id())

            dfCkp_with_id = dfCkp.withColumn(unique_id_column, F.monotonically_increasing_id())

            windowSpec = W.orderBy(unique_id_column)
            dfCkp_with_id = dfCkp_with_id.withColumn(unique_id_column, F.row_number().over(windowSpec))
            df_tmp_uuids = df_tmp_uuids.withColumn(unique_id_column, F.row_number().over(windowSpec))
            final_df = dfCkp_with_id.join(df_tmp_uuids, dfCkp_with_id[unique_id_column] == df_tmp_uuids[unique_id_column]).\
                         drop(unique_id_column)
        else: 
            final_df = dfCkp;


        first_row=data_ref[8:]+data_ref[5:7]+data_ref[:4]+"|1"
        print(f"primeira linha gerada - data\n")
        print(first_row)

        final_df_columns_list = final_df.columns
        second_row = "|".join(final_df_columns_list)
        print(f"segunda linha gerada - colunas:\n")
        print(second_row)

        # third_row_dfTb = DataFrame para salvar dados em tabelas Hive(Não pode fazer o tratamento do [n]
        third_row_dfTb = final_df.withColumn("ARQ_VALUES", spf.concat_ws("|",*final_df_columns_list));
        third_row_df = final_df.withColumn("A", spf.concat_ws("|",*final_df_columns_list));
        third_row_df = third_row_df.withColumn("ExpCkpValues",spf.expr("""replace(A,'[n]',concat(decode(unhex(hex(92)), 'US-ASCII'),'n'))"""));
        third_row = list(zip(third_row_df.select("ExpCkpValues").rdd.flatMap(lambda x: x).collect())); 

        # verificar se existe condicao - tbFileWhere
        if tbFileWhere is not None and tbFileWhere!="":
            print(f"condicao tbFileWhere: {tbFileWhere}")
            third_row_df = third_row_df.where(tbFileWhere);
            third_row_dfTb= third_row_dfTb.where(tbFileWhere);
        third_row = list(zip(third_row_df.select("ExpCkpValues").rdd.flatMap(lambda x: x).collect()));
        third_row_dfTb = list(zip(third_row_dfTb.select("ARQ_VALUES").rdd.flatMap(lambda x: x).collect()));
        print(f"terceira (ate n) linha gerada:\n")
        print(third_row[-5:])

        last_row = third_row_df.count()
        last_row = str(last_row)
        print(f"ultima linha gerada:{last_row}")

        # Salvar resultado com o nome especificado na variavel tbFile
        spark_log_table_columns = StructType([
        StructField("A",StringType(),True)])

        spark_row = [
            tuple([first_row]),
            tuple([second_row]),
            *third_row,
            tuple([last_row])];

        spark_rowTb = [
            tuple([first_row]),
            tuple([second_row]),
            *third_row_dfTb,
            tuple([last_row])];

        arqCkp = self.spark.createDataFrame(spark_row, spark_log_table_columns);
        print(f"generating {tbFile}");

        arqCkp.coalesce(1) \
        .write\
        .format("csv") \
        .option("header", "false") \
        .option("encoding", "cp1252") \
        .option("escapeQuotes","false") \
        .option("quoteAll","false") \
        .option("escape","") \
        .option("quote", "\u0000") \
        .mode("overwrite") \
        .save(pathSave)

        print("\nArquivo salvo com sucesso em: {}".format(pathSave));
        
        if((tbFile is not None ) & (tbFile !="")):
            try:
                arqCkpTb = self.spark.createDataFrame(spark_rowTb, spark_log_table_columns);
                arqCkpTb.write.format('hive').mode('overwrite').saveAsTable(tbFile);
                print(f"\nPúblico salvo na tabela [{tbFile}]");
            except:
                print(f"\nErro ao salvar tabela [{tbFile}]");
                
    def dicionario_dbs(self,strDbs,strPastaSaida = "./Export"):
        import pandas as pd
        from tqdm import tqdm
        from dadosSPF import sqlConn as s
        colunas = ["id","db","tabela","nome_fisico_do_campo_destino","nome_lógico_do_campo_destino","tipo_destino","indicador_de_campo_de_chave_primária",
                   "indicador_de_nulidade_do_campo","posição_inicial","tamanho","descrição_do_dado","dominio_ou_referencia","formato_do_campo_destino",
                   "formato_da_data_ou_timestamp","tamanho_ou_precisão_do_campo","escala_do_campo","valor_minimo_do_campo","valor_maximo_do_campo",
                   "indicação_de_pci","indicação_de_consistencia_contabil"]
        df_fim = pd.DataFrame(columns = colunas)
        lTabelas = self.execImpala(f"show tables in {strDbs};").name.to_list()
        for i in tqdm(range(len(lTabelas))):
            df = s.execImpala(f"describe {strDbs}.{lTabelas[i]};")
            df['id'] = i
            df['db'] = strDbs
            df['tabela'] = lTabelas[i]
            df = df.rename(columns={"name": "nome_fisico_do_campo_destino"})
            df["nome_lógico_do_campo_destino"] = df["nome_fisico_do_campo_destino"]
            df = df.rename(columns={"type": "tipo_destino"})
            df = df[["id","db", "tabela","nome_fisico_do_campo_destino","nome_lógico_do_campo_destino","tipo_destino"]]
            df["indicador_de_campo_de_chave_primária"] = "N/A"
            df["indicador_de_nulidade_do_campo"] = "Sim"
            df["posição_inicial"] = "N/A"
            df["tamanho"] = "N/A"
            df["descrição_do_dado"] = "IMPORTANTE"
            df["dominio_ou_referencia"] = "N/A"
            df["formato_do_campo_destino"] = df['tipo_destino']
            df["formato_da_data_ou_timestamp"] = "IMPORTANTE"
            df["tamanho_ou_precisão_do_campo"] = "IMPORTANTE"
            df["escala_do_campo"] = "IMPORTANTE"
            df["valor_minimo_do_campo"] = "N/A"
            df["valor_maximo_do_campo"] = "N/A"
            df["indicação_de_pci"] = "N/A"
            df["indicação_de_consistencia_contabil"] = "N/A"
            df_fim = pd.concat([df_fim, df],ignore_index=True)
        self.sendToCsv(df_fim,"PANDAS",strPastaSaida,"dicionario_dbs_"+strDbs)
        
    def analise_dbs(self,strDbs):
        from tqdm import tqdm
        from datetime import datetime
        from dadosSPF import sqlConn as s

        #Conectando ao impala
        impala = self.getImpala(dPrint = False)

        #listando as tabelas
        print(f"Listando tabelas do {strDbs}")
        df = self.execImpala(f"show tables in {strDbs};")
        tables = df.name.to_list()
        print(f"O {strDbs} possui {len(tables)} Tabelas")

        #listando os Owners
        lOwner, lCreate, ltrans,lSize = ([] for i in range(4))
        print(f"Listando os criadores das tabelas do {strDbs}")
        for i in tqdm(range(len(tables))):
            try:
                df_desc = self.execImpala(f"Describe formatted {strDbs}.{tables[i]}")
                tmp_owner = df_desc[df_desc["name"].str.strip() == "Owner:"]["type"].iloc[0].strip()
                A,B = df_desc[df_desc["name"].str.strip() == "CreateTime:"]["type"].iloc[0].strip().split("UTC ")
                tmp_createDate = A+B
                tmp_createDate = datetime.strptime(tmp_createDate, "%a %b %d %H:%M:%S %Y").strftime("%Y-%m-%d")

                tmp_transient = df_desc[df_desc["type"].str.strip() == "transient_lastDdlTime"]["comment"].iloc[0].strip()
                tmp_transient = datetime.fromtimestamp(int(tmp_transient)).strftime("%Y-%m-%d")

                tmp_size = self.execImpala(f"show table stats {strDbs}.{tables[i]};")["Size"].to_list()[-1]
            except:
                tmp_owner = ""
                tmp_createDate = None
                tmp_transient = None
                tmp_size = None

            lOwner.append(tmp_owner)
            lCreate.append(tmp_createDate)
            ltrans.append(tmp_transient)
            lSize.append(tmp_size)

        #organiando o dataframe
        df = df.rename(columns={"name": "Tabela"})
        df["Owner"] = lOwner
        df["createDate"] = lCreate
        df["LastTransient"] = ltrans
        df["Sandbox"] = strDbs
        df["Size"] = lSize
        df = df[["Sandbox", "Tabela", "Owner","createDate","LastTransient","Size"]]
        spark = self.getSpark()
        sdf = spark.createDataFrame(df)

        #Salvando o dataframe
        print(f"Salvando Analise do {strDbs}")
        self.saveSandbox(sdf,"analise_"+strDbs)
        
    def removerAcentos(self,df,strColuna):
        """
        df_query = s.removerAcentos(df = df_query,strColuna = 'campanha')
        
        Função para remover acentos de campos de um dataframe
        
        Parameters
        ----------
        df dataframe
            dataframe onde se encontra o campo que será removido os acentos
        strColuna str
            Nome da coluna que será removido os acentos
        """
        if str(type(df)) == """<class 'pandas.core.frame.DataFrame'>""":
            from unidecode import unidecode
            df[strColuna] = df[strColuna].apply(unidecode)
        else:
            from pyspark.sql import Row, functions as spf
            df = df.withColumn(strColuna, spf.translate(strColuna,
                                           'ãäöüẞáäčďéěíĺľňóôŕšťúůýžÄÖÜẞÁÄČĎÉĚÍĹĽŇÓÔŔŠŤÚŮÝŽ',
                                           'aaousaacdeeillnoorstuuyzAOUSAACDEEILLNOORSTUUYZ'))
        return df        
# -------------------------------------------------------------------------------------------------------------------------------
# | CLASS TOOLS
# -------------------------------------------------------------------------------------------------------------------------------

class tool():
    """
    import helpers.dadosSPF as sf
    st = sf.tool()
    
    A classe de funções uteis para trabalhar com python e dataframes 
    
    """
    def getToday(self) -> str:
        """
        getToday()
        Função que retorna o dia de hoje 
        """
        return date.today().strftime("%Y-%m-%d")
    
    def getProxDiaUtil(self,hoje = str(date.today())) -> str:
        """
        getProxDiaUtil(hoje = str(date.today()))
        Função que retorna o próximo dia util descontando feriados nacionais
        
        Parameters
        ----------
        hoje str
            Variavel com a data que deseja saber o próximo dia Útil
            por padrão essa data é hoje
            
        """
        hoje = self.dateStringToDate(hoje)
        feriados= holidays.Brazil()
        proxDia = hoje + timedelta(days=1)
        while proxDia.weekday() in holidays.WEEKEND or proxDia in feriados:
            proxDia += timedelta(days=1)
        return proxDia
    
    def getDiaDaSemana(self, hoje = str(date.today())) -> str:
        """
        getDiaDaSemana(hoje = str(date.today()))
        Função que retorna o próximo dia util descontando feriados nacionais
        
        Parameters
        ----------
        hoje str
            Variavel com a data que deseja saber o dia da semana
            por padrão essa data é hoje
            
        """
        if type(hoje) == str:
            hoje = self.dateStringToDate(hoje)
            
        cod_semana = {0:'segunda',1:'terça',2:'quarta',3:'quinta',4:'sexta',5:'sabado',6:'domingo'}
        return cod_semana[hoje.weekday()]
    
    def dateStringToDate(self, strDate = str(date.today()), strFormat = '%Y-%m-%d'):
        """
        getDiaDaSemana(hoje = str(date.today()))
        Função que retorna o próximo dia util descontando feriados nacionais
        
        Parameters
        ----------
        hoje str
            Variavel com a data que deseja saber o dia da semana
            por padrão essa data é hoje
        strFormat str
            formatação da tada a ser retornada
            
        """
        return datetime.strptime(strDate, strFormat).date()
    
    def setNumAnoMes(self,meses = -5,dt_ref = str(date.today()),dm1=True) -> str:
        """
        setNumAnoMes(self,meses = -5,dt_ref = str(date.today()),dm1=True)
        Função que retorna ANOMES (202307) alem de poder mover os meses para frente ou para trás
        
        Parameters
        ----------
        meses int
            quantidade de meses a serem movimentados
        dt_ref str
            Variavel com a data que deseja deslocar o NUMANOMES
            por padrão essa data é hoje            
        """
        dt_ref = self.dateStringToDate(dt_ref)
        if meses <0:
            meses = meses*-1
            if dm1==True:
                return (date.today() - relativedelta(months=meses) - relativedelta(day=1)).strftime('%Y%m')
            else:
                return (date.today() - relativedelta(months=meses)).strftime('%Y%m')
        else:
            if dm1==True:
                return (date.today() + relativedelta(months=meses) - relativedelta(day=1)).strftime('%Y%m')
            else:
                return (date.today() + relativedelta(months=meses)).strftime('%Y%m')
    
    def dropcol(self,df01,df02):
        """
        DFB = dropcol(df01 = DFA,df02 = DFB)
        Função para igualar as colunas entre 2 dataframes
        excluido as colunas do df02 que existem a mais do que o df01
        
        Parameters
        ----------
        df01 dataframa
            dataframa com as colunas padroes
        df02
            dataframa com as colunas a serem removidas
            
        """
        colamais=list(set(df02.columns)-set(df01.columns))
        df02=df02.drop(*colamais)
        return df02
    
    def comparacolunas(self,df01,df02):
        """
        comparacolunas(df01 = DFA,df02 = DFB)
        Função para igualar as colunas entre 2 dataframes
        mostrando as colunas que possuem divergencias entre 2 dataframes
        
        Parameters
        ----------
        df01 dataframa
            dataframa com as colunas
        df02
            dataframa com as colunas
            
        """
        print("O Dataframe 01 tem {} colunas a mais do que o df02".format(list(set(df01.columns)-set(df02.columns))))
        print("O Dataframe 02 tem {} colunas a mais do que o df01".format(list(set(df02.columns)-set(df01.columns))))    
    
    def fnCount(self,df,nmDF,dPrint=True):
        if(dPrint==True):
            print("{}:{}".format(nmDF,df.count()))
            
    def zipFolder(self,strPasta = './pastaorigem/' ,strSaida = './nomepasta/nomearquivodestino'):
        try:
            shutil.make_archive(strSaida, 'zip', strPasta)
        except Exception as e:
            print('ERRO! AO COMPACTAR A PASTA')
            print(e)
            
    def zipFile(self, arquivo,pasta):
        if pasta[-1] != '/':
            pasta = pasta + '/'
        with zipfile.ZipFile(f"{arquivo}.zip", mode="w") as archive:
            archive.write(pasta+arquivo)
    
    def unzipFile(self,arquivo ="file.zip", pasta = 'targetdir'):
        if pasta[-1] != '/':
            pasta = pasta + '/'
        try:
            with zipfile.ZipFile(arquivo,"r") as zip_ref:
                zip_ref.extractall(pasta)
        except Exception as e:
            print('ERRO! AO EXTRAIR O ARQUIVO')
            print(e)
            
    def Win_listar_grupos_e_usuarios(self):
        print("""
import os
import csv
linhas = []
os.system(f"net groups /do >> grupos496.txt")
with open("grupos496.txt","r") as g:
    g = g.read()
    lGrupos = g.split('\n')
    filtered = filter(lambda nome: 'BIG_CDP' in nome, lGrupos)
    lGrupos = list(filtered)

for i in range(len(lGrupos)):
    tempGrupos = lGrupos[i].replace('*','')
    print(tempGrupos)
    if tempGrupos != '':
        os.system(f"net groups {tempGrupos} /do >> temp496.txt")
        with open("temp496.txt", "r") as ping:
            a =ping.read()
            a = a.split('\n-------------------------------------------------------------------------------\n')[-1]
            a = a.replace('\nThe command completed successfully.\n\n','').strip().replace('\n','').replace('                  ',',')
            a = a.replace('        ',',')
            a = a.replace('The command completed successfully.','Sem Usuários')
            usr_list = a.split(',')

        for us in range(len(usr_list)):
            usr_list[us] = usr_list[us].strip()
            valor = []
            valor.append(tempGrupos)
            valor.append(usr_list[us])
            linhas.append(valor)

csvColunas = ['Grupo', 'Usuario']
csvLinhas=linhas
with open('Lista de usuarios BIG_CDP.csv', 'w', newline='') as file:
    writer = csv.writer(file,delimiter=';')
    writer.writerow(csvColunas)
    writer.writerows(csvLinhas)
os.remove("temp496.txt")
os.remove("grupos496.txt")
                """)
        
        
# -------------------------------------------------------------------------------------------------------------------------------
# | CLASS DtIngestValidation [CRM]
# -------------------------------------------------------------------------------------------------------------------------------
            
class DtIngestValidation(object):    

    def __init__(self, sql_context):
        self.db_name = ""
        self.table_name = ""
        self.sqlc = sql_context
        self._current_date = datetime.now().date()

    def get_dt_ingest(self):
        max_dt_ingest=self.sqlc.sql(f"SHOW PARTITIONS {self.db_name}.{self.table_name}").collect()
        last_partition = max_dt_ingest[len(max_dt_ingest)-1]["partition"][10:20]

        return last_partition
    
    def is_dt_ingest_valid(self):      
        date_var = datetime.strptime(self.get_dt_ingest(),'%Y-%m-%d').date()

        print('INFO: current_date {0}'.format(self._current_date))
        print(f'INFO: last dt_ingest from {self.db_name}.{self.table_name}: {date_var}')

        if (self._current_date > date_var):
            return False
        
        return True 
    
    def check_ingest(self, db_name, table_name):

        self.db_name = db_name
        self.table_name = table_name
        attempts = 1
        success = False
        time_count = 1800

        while((attempts <= 4) & (success == False)):
            if attempts == 4:
                print(f"ERROR: Não foi possível realizar a operação devido a falta de ingestão na tabela {self.db_name}.{self.table_name}")

                raise Exception
            
            print(f"INFO: Tentativa de execução {attempts}")

            try:                
                isValid = self.is_dt_ingest_valid()

                if(isValid):
                    print("INFO: A ingestão foi realizada hoje!")

                    success = True
                    break
                else:
                    print("INFO: A ingestão ainda não ocorreu")

                    success = False
                    attempts = attempts + 1
                    time.sleep(time_count)

            except:
                print('ERROR: Falha na verificação da ingestão. Uma nova tentativa será feita!')
                attempts = attempts + 1
                time.sleep(time_count);

    def ckpLay1(self,dfCkp,pathSave,tbFile=None, tbFileWhere=None,data_ref=datetime.today().date().strftime("%Y-%m-%d")):

        # verificar se ja existe o campo COD_CRM, se nao existir precisa adicionar o UUID
        if "cod_crm" not in list(map(lambda x: x.lower(),dfCkp.columns)):
            # GERAR UUID
            unique_id_column = "unique_id_to_merge"

            all_uuids = [(str(uuid.uuid4()),) for x in range(0,dfCkp.count())]
            df_tmp_uuids = self.spark.createDataFrame(all_uuids, ['COD_CRM'])

            # monotonically_increasing_id nao esta gerando ids consecutivos.
            df_tmp_uuids = df_tmp_uuids.withColumn(unique_id_column, F.monotonically_increasing_id())

            dfCkp_with_id = dfCkp.withColumn(unique_id_column, F.monotonically_increasing_id())

            windowSpec = W.orderBy(unique_id_column)
            dfCkp_with_id = dfCkp_with_id.withColumn(unique_id_column, F.row_number().over(windowSpec))
            df_tmp_uuids = df_tmp_uuids.withColumn(unique_id_column, F.row_number().over(windowSpec))
            final_df = dfCkp_with_id.join(df_tmp_uuids, dfCkp_with_id[unique_id_column] == df_tmp_uuids[unique_id_column]).\
                         drop(unique_id_column)
        else: 
            final_df = dfCkp;


        first_row=data_ref[8:]+data_ref[5:7]+data_ref[:4]+"|1"
        print(f"primeira linha gerada - data\n")
        print(first_row)

        final_df_columns_list = final_df.columns
        second_row = "|".join(final_df_columns_list)
        print(f"segunda linha gerada - colunas:\n")
        print(second_row)

        # third_row_dfTb = DataFrame para salvar dados em tabelas Hive(Não pode fazer o tratamento do [n]
        third_row_dfTb = final_df.withColumn("ARQ_VALUES", spf.concat_ws("|",*final_df_columns_list));
        third_row_df = final_df.withColumn("A", spf.concat_ws("|",*final_df_columns_list));
        third_row_df = third_row_df.withColumn("ExpCkpValues",spf.expr("""replace(A,'[n]',concat(decode(unhex(hex(92)), 'US-ASCII'),'n'))"""));
        third_row = list(zip(third_row_df.select("ExpCkpValues").rdd.flatMap(lambda x: x).collect())); 


        # verificar se existe condicao - tbFileWhere
        if tbFileWhere is not None and tbFileWhere!="":
            print(f"condicao tbFileWhere: {tbFileWhere}")
            third_row_df = third_row_df.where(tbFileWhere);
            third_row_dfTb= third_row_dfTb.where(tbFileWhere);
        third_row = list(zip(third_row_df.select("ExpCkpValues").rdd.flatMap(lambda x: x).collect()));
        third_row_dfTb = list(zip(third_row_dfTb.select("ARQ_VALUES").rdd.flatMap(lambda x: x).collect()));
        print(f"terceira (ate n) linha gerada:\n")
        print(third_row[-5:])

        last_row = third_row_df.count()
        last_row = str(last_row)
        print(f"ultima linha gerada:{last_row}")

        # Salvar resultado com o nome especificado na variavel tbFile
        spark_log_table_columns = StructType([
        StructField("A",StringType(),True)])

        spark_row = [
            tuple([first_row]),
            tuple([second_row]),
            *third_row,
            tuple([last_row])];

        spark_rowTb = [
            tuple([first_row]),
            tuple([second_row]),
            *third_row_dfTb,
            tuple([last_row])];

        arqCkp = self.spark.createDataFrame(spark_row, spark_log_table_columns);
        print(f"generating {tbFile}");

        arqCkp.coalesce(1) \
        .write\
        .format("csv") \
        .option("header", "false") \
        .option("encoding", "cp1252") \
        .option("escapeQuotes","false") \
        .option("quoteAll","false") \
        .option("escape","") \
        .option("quote", "\u0000") \
        .mode("overwrite") \
        .save(pathSave)

        print("\nArquivo salvo com sucesso em: {}".format(pathSave));
        
        if((tbFile is not None ) & (tbFile !="")):
            try:
                arqCkpTb = self.spark.createDataFrame(spark_rowTb, spark_log_table_columns);
                arqCkpTb.write.format('hive').mode('overwrite').saveAsTable(tbFile);
                print(f"\nPúblico salvo na tabela [{tbFile}]");
            except:
                print(f"\nErro ao salvar tabela [{tbFile}]");
                
# -------------------------------------------------------------------------------------------------------------------------------
# | EASY IMPORTS
# -------------------------------------------------------------------------------------------------------------------------------                                
sqlConn =  conn()
tools = tool()
whoami = """
__author__ =     "CARLOS PIVETA"
"""