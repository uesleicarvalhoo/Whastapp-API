import json
from api_wrapper import WhatsWrapper
from flask import Flask, request, jsonify, send_file


wrapper = WhatsWrapper('Ueslei')
app = Flask(__name__)


@app.route('/qrcode/', methods=['GET'])
def qr_code():
    if request.method == 'GET':
        if not wrapper.logado():
            return send_file(wrapper.retornar_qr())

        else:
            response = {
                'status': 'falha',
                'mensagem': 'Usuario já logado'
                }

    return jsonif(response)

@app.route('/mensagem/', methods=['GET', 'POST'])
def mensagem():
    if wrapper.logado():
        if request.method == 'POST':
            print(request.data)
            dados = json.loads(request.data)
            contato = dados.get('contato', None)
            text = dados.get('text', None)
            midia = dados.get('midia', None)
            
            response = wrapper.enviar_msg_contato(contato, text, midia)

        elif request.method == 'GET':
            msg = wrapper.retornar_msg_nova()

            response = {
                'status': 'sucesso',
                'mensagem': msg
                }

    else:
        response = {
            'status': 'falha',
            'mensagem': 'Conexão não estabelecida, aguarde '
        }

    return jsonify(response)

@app.route('/')
def home():
    if wrapper.logado():
        status = 'Whatswapp Web logado!'

    else:
        status = 'Whatsapp não conectado, valide o QrCode para continuar.'

    response = {
        'Autor': 'Ueslei Carvalho de Oliveira',
        'e-mail': 'uesleicdoliveira@gmail.com',
        'whtasapp': '5571991018505',
        'instagram': '',
        'linkedin': '',
        'status': status
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run()
