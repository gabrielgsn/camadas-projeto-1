#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from enlace import *
import time
import numpy as np
import sys
import struct
import random
# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)

def cria_Head(msg_type, i, payload_len, len_payload):
    head = msg_type.to_bytes(2, byteorder='big')
    head += i.to_bytes(2, byteorder='big')
    head += payload_len.to_bytes(2, byteorder='big')
    head += len_payload.to_bytes(2, byteorder='big')
    head += b'\x00'*4
    return head

def cria_payload(payload):
    payload_bytes = b''
    for byte in payload:
        payload_bytes += byte.to_bytes(1, byteorder='big')
    return payload_bytes

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        # time.sleep(2)
        # com1.sendData(b'00')
        # time.sleep(1)


        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são um array bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.

        # Projeto 3

        # HANDSHAKE
        head = b'\x00'*12
        eop = b'\xFF\xFF\xFF'
        txBuffer = head + eop
        print("Enviando handshake...")
        com1.sendData(txBuffer)

        init_time = time.time()
        while True:
            len_rxBuffer = com1.rx.getBufferLen()
            if len_rxBuffer > 0:
                rxBuffer, _ = com1.getData(15)
                if rxBuffer == txBuffer:
                    print("Handshake recebido")
                    break
            if time.time() - init_time > 5:
                continar = input("Servidor inativo. Tentar novamente? (S/N)")
                if continar == 'N':
                    print("Encerrando comunicação")
                    com1.disable()
                    sys.exit()
                else:
                    print("Enviando handshake...")
                    com1.sendData(txBuffer)
                    init_time = time.time()


   # Criando os pacotes
        pk = './imgs/paulo_kogos.jpg'
        pk_bytes = open(pk, 'rb').read()
        pk_size = len(pk_bytes)
        print(f'Tamanho da imagem: {pk_size} bytes')

        payload_list = []
        payload = []
        for byte in pk_bytes:
            if len(payload) < 50:
                payload.append(byte)
            else:
                payload_list.append(payload)
                payload = []
                payload.append(byte)
        payload_list.append(payload)
        payload_len = len(payload_list)
        print(f'Quantidade de pacotes: {payload_len}')
        print("Enviando dados ....")

        for i, payload in enumerate(payload_list):
            payload_bytes = cria_payload(payload)
            if i+1 < payload_len:
                len_payload=len(payload_list[i+1])
            else:
                len_payload=0
            head = cria_Head(2, i, payload_len, len_payload)
            eop = b'\xFF\xFF\xFF'
            txBuffer = head + payload_bytes + eop
            print(f'Enviando pacote {i}')
            com1.sendData(txBuffer)
            time.sleep(0.2)
            init_time = time.time()
            
            while True:
                len_rxBuffer = com1.rx.getBufferLen()
                if len_rxBuffer > 0:
                    rxBuffer, nRx = com1.getData(12)
                    confirmacao=cria_Head(0, i, 0, 0)
                    erro=cria_Head(1, i, 0, 0)
                    if rxBuffer == confirmacao:
                        print(f'Pacote {i} recebido')
                        break
                    elif rxBuffer == erro:
                        print(f'Erro no pacote {i}')
                        print(f'Reenviando pacote {i}')
                        com1.sendData(txBuffer)
                        time.sleep(0.2)
                    elif rxBuffer == b'\x00'*12:
                        print('Todos os pacotes recebidos')
                        print("encerrando comunicação")
                        break
                if time.time() - init_time > 5:
                    print(f'Tempo limite excedido para o pacote {i}')
                    print(f'Reenviando pacote {i}')
                    com1.sendData(txBuffer)
                    time.sleep(0.2)
                    init_time = time.time()

                
  
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        
        # #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        # #Veja o que faz a funcao do enlaceRX  getBufferLen

        # #acesso aos bytes recebidos        
            
        # # PROJETO 1
        # # f = open(imgW, 'wb')
        # # f.write(rxBuffer)
        # # f.close()

        # # print("Salvando a Imagem lida")

        # for i in range(len(rxBuffer)):
        #     print("recebeu {}" .format(rxBuffer[i]))
        
        # Encerra comunicação

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
