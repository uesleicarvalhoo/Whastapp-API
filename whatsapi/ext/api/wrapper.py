import os
import tempfile
import contextlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoAlertPresentException, NoAlertPresentException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageOps


class WhatsWrapper:
    SELECTORS = {
        'qrcode': 'canvas[aria-label="Scan me!"]',
        'anexo': 'span[data-icon="clip"]',
        'add_midia': 'input[type="file"]',
        'bt_enviar': 'span[data-icon="send"]',
        'alerta_msg': 'span[class="_31gEB"]',
        'painel_msgs': 'div[id="pane-side"]',
        'msg_conversa': 'div[class="_2hqOq message-in focusable-list-item"]',
        'texto_msg': 'span[class="_3Whw5 selectable-text invisible-space copyable-text"]'
        }

    CLASSES = {
        'reload_qr': '_3IKPF',
        'painel_qrcode': '_1QMFu',
        'poup-contato': 'G_MLO',
        'bt_enviar_midia': '_6TTaR',
        'nova_msg': '_31gEB',
        'caixa_texto': '_3uMse'
        }

    url_msg = 'https://web.whatsapp.com/send?1=pt_BR&phone=%s'

    def __init__(self, usuario: str):
        options = webdriver.ChromeOptions()
        options.add_argument('user-data-dir=./web')
        #options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-log')
        options.add_argument('--loglevel=3')
        #options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3312.0 Safari/537.36') 

        self.usuario = usuario
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('https://web.whatsapp.com/')

    def logado(self)->bool:
        """Verifica se o usuario já está logado no WhatsappWeb

        Returns:
            bool: True caso o usuario esteja logado e False caso esteja deslogado
        """

        self.driver.save_screenshot('driver.png')
        try:
            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['painel_msgs'])))

        except TimeoutException:
            try:
                WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CLASS_NAME, self.CLASSES['painel_qrcode'])))

            except TimeoutException:
                self.logado()

            else:
                return False

        else:
            return True

    def recarregar_qr(self):
        self.driver.find_element_by_class_name(self.CLASSES['reload_qr']).click()

    def retornar_qr(self)->str:
        """Salva a imagem do QRCode

        Returns:
            str: Caminho para a imagem salva
        """
        if 'Clique para carregar o código QR novamente' in self.driver.page_source or 'Click to reload QR code' in self.driver.page_source:
            self.recarregar_qr()

        qr = self.driver.find_element_by_css_selector(self.SELECTORS['qrcode'])
        ActionChains(self.driver).move_to_element(qr).perform()

        pasta, qr_png = tempfile.mkstemp(prefix=f'{self.usuario}', suffix='.png')
        qr.screenshot(qr_png)
        os.close(pasta)

        qr = ImageOps.expand(Image.open(qr_png), border=50, fill='white')
        qr.save(qr_png)

        return qr_png

    def validar_contato(self, numero: str)->bool:
        """Verifica se o número informado possui whatsapp

        Args:
            numero (str): numero para verificar

        Returns:
            bool: True caso o contato possua um número valido e False caso não possua
        """
        url = self.url_msg % numero

        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['painel_msgs'])))
            try:
                self.driver.find_elements_by_class_name(self.CLASSES['poup-contato'])

            except NoSuchElementException:
                return True
            
            else:
                return False

        except TimeoutException:
            self.validar_contato(numero)

    def enviar_msg_contato(self, contato:str, txt:str=None, midia:str=None)->dict:
        """Envia mensagem para o contato especificado

        Args:
            contato (str): Numero do contato
            txt (str, optional): Texto para enviar a mensagem. Defaults to None.
            midia (str, optional): Caminho completo para a midia (imagem ou video). Defaults to None.

        Returns:
            dict: Dict com os status do envio da mensagem
        """ 
        if txt == None and midia == None:
            response = {'status': False, 'mensagem': 'Nenhuma midia ou mensagem informada'}

        else:
            self.iniciar_conversa(contato, txt)

            if not midia == None and os.path.isfile(midia):
                self.anexar_midia(midia)
                response = {'status': True, 'mensagem': 'Mensagem enviada com sucesso!', 'text': txt, 'midia': midia}

            else:
                self.driver.find_element_by_css_selector(self.SELECTORS['bt_enviar']).click()
                response = {'status': True, 'mensagem': 'Mensagem enviada com sucesso!', 'text': txt, 'midia': midia}

        return response

    def anexar_midia(self, midia:str, enviar:bool=True):
        self.driver.find_element_by_css_selector(self.SELECTORS['anexo']).click()

        add_midia = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['add_midia'])))
        add_midia.send_keys(midia)

        if enviar:
            bt_enviar = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, self.CLASSES['bt_enviar_midia'])))
            bt_enviar.click()

    def enviar_msg(self, txt:str=None, midia:str=None)->dict:
        """Envia uma mensagem para o contato atual

        Args:
            txt (str, optional): Texto da mensagem que deve ser enviada. Defaults to None.
            midia (str, optional): Caminho completo para a midia. Defaults to None.

        Returns:
            dict: Dicionario com os status da mensagem
        """

        if txt == None and midia == None:
            response = {'status': False, 'mensagem': 'Nenhuma midia ou mensagem informada'}

        else:
            if not txt == None:
                cx_msg = self.driver.find_elements_by_class_name(self.CLASSES['caixa_texto'])

                for linha in txt.split('\n'):
                    cx_msg.send_keys(linha)
                    webdriver.ActionChains(cx_msg).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
            
            if not midia == None and os.path.isfile(midia):
                self.anexar_midia(midia)
            
            else:
                self.driver.find_element_by_css_selector(self.SELECTORS['bt_enviar']).click()

            response = {'status': True, 'mensagem': 'Mensagem enviada com sucesso!', 'text': txt, 'midia': midia}

        return response

    def iniciar_conversa(self, contato:str, txt:str=None):
        """Incia a conversa com o contato especificado

        Args:
            contato (str): Numero do contato
            txt (str, optional): Texto para iniciar a conversa. Defaults to None.
        """
        url = self.url_msg % contato

        if not txt == None:
            txt = txt.strip().replace(' ', '%20').replace('\n', '%0A')
            url += '&text=%s' % txt

        self.driver.get(url)

        try:
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.SELECTORS['painel_msgs'])))

        except TimeoutException:
            self.iniciar_conversa(contato)

    def retornar_mensagens(self)->list:
        "Retorna um dicionario com as mensagens enviadas pelo contato (numero) e pela pessoa"
        mensagens = list(dict())
        return mensagens

    def retornar_msg_nova(self)->str:
        """Verifica todas as conversas que contem mensagens não lidas e retorna o elemento

        Returns:
            webdriver: Elemento da conversa que contem mensagens não lidas
        """

        response = None
        for msg in self.driver.find_elements_by_css_selector(self.SELECTORS['painel_msgs']):
            with contextlib.suppress(NoSuchElementException, StaleElementReferenceException):
                self.driver.find_element_by_css_selector(self.SELECTORS['alerta_msg'])
                msg.click()
                response = self.retornar_ultima_msg()
                break

        return response

    def retornar_ultima_msg(self)->str:
        """Verifica a última mensagem enviada pelo contato

        Returns:
            str: Ultima mensagem enviada pelo contato
        """
        ultima_msg = None
        for msg in self.driver.find_elements_by_css_selector(self.SELECTORS['msg_conversa']):
            with contextlib.suppress(NoSuchElementException, StaleElementReferenceException):
                text = msg.find_element_by_css_selector(self.SELECTORS['texto_msg']).text
                if not text == None:
                    ultima_msg = text

        return ultima_msg

