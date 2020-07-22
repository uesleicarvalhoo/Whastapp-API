from src import api

if __name__ == "__main__":
    app = api.create_app()
    app.run()



    """
        Cada bot terá a sua propria configuração, vou vender/alugar de acordo com a necessidade de cada cliente
        O acesso ao bot será por meio de uma API e cada cliente vai ter o bot hospedado em um servidor diferente
        O bot validará os status do cliente de acordo com um banco de dados MySQL que vou ter na WEB contendo o login, senha e status da assinatura
        Começar o processamento pelo banco de dados, exemplo consultar informações (consulta, agendamento, datas disponíveis) ou inserir dados (confirmar consulta, realizar venda, cadastrar)
        Caso o banco de dados não realize nenhuma tratativa o controle será passado para o tratamento de texto
        Verificar forma de realizar a consulta no banco de dados

    """

