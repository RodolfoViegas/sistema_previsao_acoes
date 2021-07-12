# Sistema Distribuido para previsão de Ações

Este projeto visa à contrução de um Sistema Distribuído do tipo Nuvem para a previsão de preço de Ações do Mercado Financeiro. 

As ferramentas utilizadas na construção deste sistema são os serviços da AWS, sistema de cron job EasyCron e a API Pytorch. Da AWS foram utilizados: Duas funções Lambda, Kinesis Data Stream, Bucket S3, EFS, EC2, duas APIs REST Gateways.


A arquitetura do preojeto se dá com a operação cron Job, via EasyCron, em que são feitas chmadas do método HTTP POST que envia um arquivo .json com o nome da ação desejada (para este caso ação da Apple) à primeira função Lambda. Esta, por sua vez, chama os dados do dia anterior (dada limitações de requisições em tempo real, que são pagas, a API somente oferece dados até um dia antes da chamada) através da API Pandas Data Reader. veri
