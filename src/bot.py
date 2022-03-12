from src.schemas.message import MessageInput
from src.talkers import whatsapp_talker as talker

contacts = []


@talker.call_on_unread_message()
def send_response(msg: MessageInput):
    if msg.contact not in contacts:
        text = "Bem vindo a sorveteria 3 estrelas!\nSegue o nosso cardarpio"

    else:
        contacts.append(msg.contact)
        text = "Segue o cardapio:"

    talker.send_message(MessageInput(**{"contact": msg.contact, "text": text}))


def main_loop():
    talker.loop_to_check_unread_messages()
