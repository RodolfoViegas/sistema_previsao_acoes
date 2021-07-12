import pandas_datareader.data as web
import json
import boto3
import datetime
import pandas as pd


""" Dada limitações da API alpha vantage em entregar dados em tempo real, esta previsão será para dia anteriores (dados em tempora real são pagos)
A recomendação àqueles que desejarem utilizar este código é que treinem vossos modelos até um dia antes da previsão, isto é, até o "anteontem" e mudem 
a string de formato de tempo para o dia anterior do teste.
PAra os que tiverem pago a alpha vantange, modifica a string abaixo para os valores comentados ao lado, estes converterão o horário atual, em vez de somente
às horas."""

# tempo atual
agora = datetime.datetime.now()
# reduz um dia para coletar os valores do dia anterior (os que são disponíveis, como explicado)
agora = agora - - datetime.timedelta(days=1)

# O terá como fixos 1 minutos e 00 segundos, podendo ser modificaos para outra frequência de previsão
agora = agora.strftime("%Y-%m-%d %H:01:00")#"%Y-%m-%d


data_hora = agora.split(' ')



def lambda_handler(event, context):
    
    # A API boto3 é a responsvel pela comunição dos dados entre serviços, no caso bucket S3 e kinesis Data Stream.
    S3 = boto3.client('s3','us-east-1')
    client = boto3.client('kinesis')
    
#A API Pandas DataReader, que é interface à API alpha Vantage, recebe como parâmetros: símbolo da ação, o horário e a chave da conta, para a coleta de dados.

    df = web.DataReader('AAPL", 
                        "av-intraday", 
                        start=data_hora[0],
                        api_key='BNYLT38LCDB0TBWF')# o símbolo AAPL é para as ações da empresa Apple, caso queira mudá-lo retreine o modelo em função da nova ação.
    

   
    try:
        # O valor e data desejados são convertidos a objetos do tipo json para o envio.
        parsed = json.dumps({"data":data_hora[0] + ' ' + data_hora[1],
                            "preco":df['close'].loc[data_hora[0] + ' ' + data_hora[1]]})
    
    # caso os valor em minutos não exista, esta função lambda manda diretamente ao armazenador S3 uma mensagem de "sem valor" com a dada e hora como chaves.
    
    except KeyError:
        data_chave = str(datetime.datetime.strptime(data_hora[0] + ' ' + data_hora[1],"%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=15))
        parsed= bytes(json.dumps({"data":data_chave, "preco":"sem valor"}).encode('UTF-8'))
        
        S3.put_object(Body=parsed,
                            Bucket="previsoes",
                            Key=data_chave)
        return '{"Status":"200", "preco": "sem valor"}'

    
    # Existindo a dada, esta manda ao Kinesis Data Stream, este redirecionará os dados a próxima função Lambda com a rede neural para previsão.
    # O método abaixo tem parâmetros: DataStream, que é nome do Kinesis Data Stream para o qual os dados serão enviádos, Data são os dados em si e
    # PartitionKey é um valor de identificação do fluxo enviado.
    
    client.put_record(StreamName='precos_apple',
                         Data=parsed, PartitionKey="part_key")
                         
    return '{"Status":"200","valor": "enviado a rede neural"}'
