import requests
"""
Códido simples para acessar os dados criados num bucket S3 que acumular previsões feitas pela segunda Lmabda. 
Este código realiza uma operação HTTP GET numa API Gateway conectada ao bucket.
"""

print("Acesso a dados de previsão em tempo real")

condicao_de_parada=1

while condicao_de_parada !=0 :

    """São lidas pleno teclado a data, ano, mês e dia, e hora, hora e minutos, segundos não são necessários. Se existir previsão
    essa será retornado; senão a mensagem 'sem valor'.
     """


    data = input("Digite o ano, mês e dia nesta forma AAAA-MM-DD: ")
    hora = input("Digite a hora e minuto neste formato HH:MM: ")

    data_hora = data + " " + hora
    valor = requests.get('https://zlpscxdwdj.execute-api.us-east-1.amazonaws.com/v1/previsoes/'+data_hora+":00")
    print(valor.content)
    
    condicao_de_parada = input('Digite 0 para sair ou qualquer outro caractere para continuar: ')
    if condicao_de_parada == '0':
        break
