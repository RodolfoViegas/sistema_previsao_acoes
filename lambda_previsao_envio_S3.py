import torch
import datetime
import boto3
import json
import numpy as np
from pickle import load
import base64
import boto3
import sklearn
import warnings
warnings.filterwarnings('error')
try:
   import sklearn 
except Warning:
   pass
   
class LSTM(torch.nn.Module):
    def __init__(self, input_size=1, hidden_layer_size=75, output_size=1,num_layers=2):
        super().__init__()
        self.hidden_layer_size = hidden_layer_size

        self.lstm = torch.nn.LSTM(input_size, hidden_layer_size)

        self.linear = torch.nn.Linear(hidden_layer_size, output_size)

        self.hidden_cell = (torch.zeros(1,1,self.hidden_layer_size),
                            torch.zeros(1,1,self.hidden_layer_size)) 

    def forward(self, input_seq):
        lstm_out, self.hidden_cell = self.lstm(input_seq.view(len(input_seq) ,1, -1), self.hidden_cell)
        predictions = self.linear(lstm_out.view(len(input_seq), -1))
        return predictions[-1]
        y_pred = self.linear(
            lstm_out.view(self.input_dim, len(inputs), self.hidden_dim)[-1]
        )
        return y_pred
        
       
        

with open('/mnt/ml/lib/scaler.pkl', 'rb') as file:
    scaler = load(file) 

# "instanciação" dos objetos para manipular o S3 e a Rede 
client = boto3.client('s3','us-east-1')#,config=botocore.config.Config(s3={'addressing_style':'path'}))

model = LSTM() 

# Pelo teste é preciso espeficicar o caminho da variável de ambiente

model.load_state_dict(torch.load('/mnt/ml/lib/model_dict_torch_lstm_apple.pth'))
model.eval()


def lambda_handler(event, context):
    
    # recebe o valor de data stream  e decodifica-o
    for record in event["Records"]:
        decoded_data = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
    
    
    # Fragmentação da string para retirada do valor preço (estranhamente o uso da conversão de json para dict passou a dar erro 
    data = json.loads(decoded_data)
    
    

    # modificação da forma do tensor para as operações a seguir
    X = np.array([data['preco']]).reshape(-1,1).astype('float')
    
    # tranformação logaritma e normalização
    X_scaled = scaler.transform(np.log(X))

    # teste na rede
    with torch.no_grad():
        pred = model.forward(torch.Tensor(X_scaled))
    
    # aqui o valor volta à escala pré-normalização e volta da traformação logarítmica
    parsed = np.exp(scaler.inverse_transform(pred.view(-1,1)))
    
    
    # Criação de um objeto datetime que marca da hora em mais 15 minutos para a previsão
    data_chave = str(datetime.datetime.strptime(data['data'],"%Y-%m-%d %H:%M:%S") + datetime.timedelta(minutes=15))

  
    #Transformação de em Json com a data (com chave 'data') que o valor chega mais um sinal mais 15 minutos que correspondo ao preço ('preço')
    
    parsed= bytes(str(parsed.item()), encoding='utf8')
    
    #parsed= bytes(json.dumps({"preco":str(parsed.item())}).encode('UTF-8'))#"data":data_chave, 
    
        
    # envio ao Bucket S3
    return client.put_object(Body=parsed,
                            Bucket="previsoes",
                            Key=data_chave)
    
