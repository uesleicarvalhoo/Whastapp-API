from src.wrapper import WhatsWrapper
from src.bot_treatment import BotTreatment

class WhatsBot:
    bot_atendimento = True
    enviar_mensagens = True
    mensagens_pendentes = list()

    def __init__(self, usuario:str):
        self.usuario = usuario
        self.wrapper = WhatsWrapper(usuario)
        self.treatment = BotTreatment()

    def mainloop(self):
        while True:
            if not self.wrapper.logado():
                continue

            if self.bot_atendimento:
                for conversa in self.wrapper.retornar_novas_msgs():
                    conversa.click()
                    ultima_msg =  self.wrapper.retornar_ultima_msg()
                    msg_retorno = self.treatment.processar_msg(ultima_msg)
                    self.wrapper.enviar_msg(msg_retorno)

            if self.enviar_mensagens:
                for msg in self.mensagens_pendentes:
                    if not self.pausar_envio:
                        break
                
                    txt = msg.get('text', None)
                    midia = msg.get('midia', None)
                    contato = msg.get('contato', None)

                    if not contato == None and not (txt == None and midia == None):
                        self.wrapper.enviar_msg_contato(contato, txt, midia)

    def enviar_msg(self, contato:int, text:str=None, midia:str=None):
        self.mensagens_pendentes.append({'contato': contato, 'text': text, 'midia': midia})

    def atualizar_envio_msg(self, enviar_msg:bool):
        self.enviar_mensagens = enviar_msg

    def atualizar_bot_atendimento(self, auto_atendimento:bool):
        self.bot_atendimento = auto_atendimento


class WhatsContact:
    def __init__(self, numero:int, nome:str):
        self.__numero = numero
        self.__nome = nome

    @property
    def ultima_msg(self):
        self.__ultima_msg

    @property
    def nome(self):
        return self.__nome
    
    @property
    def numero(self):
        return self.__numero

    def set_ultima_msg(self, msg):
        self.__ultima_msg = msg

    @WhatsBot.driver_need
    def enviar_msg(self, texto='', midia=''):

    def __str__(self):
        return f'<<WhatsObject-{self.numero}>>'




