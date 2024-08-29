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
serialName = "COM4"                  # Windows(variacao de)

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
        
        # Enviando pacotes
        # Pacotes comecando com 2 sao envios de dados
        # Pacotes comecando com 1 sao de confirmacao
        for i, payload in enumerate(payload_list):
            head = struct.pack('i', 2)
            head += struct.pack('i', i)
            head += struct.pack('i', payload_len)
            head += struct.pack('i', len(payload))
            head += b'\x00'*8
            eop = b'\xFF\xFF\xFF'
            txBuffer = head + payload + eop
            print(f'Enviando pacote {i}')
            com1.sendData(txBuffer)
            time.sleep(0.1)
        head = b'\x00'*4

        
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        print("enviando dados ....")
        
        
        
        
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        time.sleep(2)
        com1.tx.threadMutex = True
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.

        print("Recebendo dados ....")
        
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
