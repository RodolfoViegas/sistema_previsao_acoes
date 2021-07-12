# Sistema Distribuido para previsão de Ações

Este projeto visa à contrução de um Sistema Distribuído do tipo Nuvem para a previsão de preço de Ações do Mercado Financeiro. 

As ferramentas utilizadas na construção deste sistema são os serviços da AWS, sistema de cron job EasyCron e a API Pytorch. Da AWS foram utilizados: Duas funções Lambda, Kinesis Data Stream, Bucket S3, EFS, EC2, duas APIs REST Gateways.


A arquitetura do projeto inicia com a operação cron job, via o serviçoEasyCron, em que são feitas chamadas do método HTTP GET, simplesmente retornando a execução da primeira função Lambda. Esta, por sua vez, chama os dados do dia anterior (dada limitações de requisições em tempo real, que são pagas, a API somente oferece dados até um dia antes da chamada) através da API Pandas Data Reader. A chamadas cron são de hora em hora. A primeira função Lambda, ao coletar os dados, verifica se há valor par a data e hora específicos, caso existe, esse é enviado ao Kinesis Data Stream, senão, é enviado ao bucker S3 com uma mensagem de "sem valor".

A hora com valor é enviada no formato de um objeto json ao srviço Data Stream (forma: '{"data": "2021-07-05", "preco": "120"}'). O Data Stream é um gerenciador de fluxos de consegue lidar com uma grande carga de dados e direcionando-os aos outros serviços, neste exemplo os valores serão enviados à segunda Lambda. 

Essa, ao receber um novo preço, instancia um modelo de rede neural que está localizado dentro do serviço EFS (juntos com a biblioteca Pytorch, é possível outras formas de enviar as bibliotecas necessárias para uso de Lambda como contêineres Docker) realiza a previsão para o valor 15 minutos após o horário e envia ao bucket S3.

Para a analizar os valores contindos no S3 podemos usar o console AWS ou um simples código python neste trabalho que chama uma segunda API e faz consultas de GET retornando o valor.
