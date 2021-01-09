import json
from fuzzywuzzy import process, fuzz


class BotTreatment:
    def __init__(self):
        self.text_treatment = TextTreatment()
        self.db_treatment = DatabaseTreatment()

    def processar_msg(self, msg:str)->str:
        resposta = self.db_treatment.processar_msg(msg)

        if resposta == None:
            resposta = self.text_treatment.processar_msg(msg)

        return resposta


class TextTreatment:
    def __init__(self):
        self.carregar_respostas()

    def carregar_respostas(self):
        self.respostas = dict()
        with open('./config/talk.JSON', encoding='utf-8') as talk_json:
            self.respostas = json.load(talk_json)

    def processar_msg(self, msg:str)->str:
        item_corresp = match_msg(msg, self.respostas)
        resposta = self.respostas.get(item_corresp, 'Eu ainda não tenho uma resposta para essa pergunta. Pode tentar perguntar de outra forma?')

        return resposta


class DatabaseTreatment:
    def __init__(self):
        pass

    def processar_msg(self, msg):
        return None


def match_msg(msg:str, itens:list, acerto_min=90):
    """Verifica qual elemento da lista se assemelha mais com a opção indicada de acordo com a taxa de acerto informada

    Args:
        msg (str): mensagem que deve ser procurada
        itens (list): lista ou objeto iteravel para verificar a compatibilidade
        acerto_min (int, optional): Valor minimo de correspondencia. Defaults to 90.

    Returns:
        str: String que mais corresponde a opção escolhida, None caso a correspondencia seja menor que a minima indicada
    """

    msg = msg.lower()
    itens = [i.lower() for i in itens]

    if msg in itens:
        return itens[itens.index(msg)]

    msg_retorno, acerto = process.extractOne(msg.lower(), itens)

    if acerto >= acerto_min:
        #print('process.extractOne:', acerto)
        return msg_retorno

    for i in itens:
        #print('item:', i, 'fuzz.ratio:', fuzz.ratio(msg, i))
        if fuzz.ratio(msg, i) >= acerto_min:
            return i

    for i in itens:
        #print('item:', i, 'fuzz.partial_ratio:', fuzz.partial_ratio(msg, i))
        if fuzz.partial_ratio(msg, i) >= acerto_min:
            return i
    
    for i in itens:
        #print('item:', i, 'fuzz.sort_ratio:', fuzz.token_sort_ratio(msg, i))
        if fuzz.token_sort_ratio(msg, i) >= acerto_min:
            return i
    
    for i in itens:
        #print('item:', i, 'fuzz.token_set_ratio:', fuzz.token_set_ratio(msg, i))
        if fuzz.token_set_ratio(msg, i) >= acerto_min:
            return i

    return None


