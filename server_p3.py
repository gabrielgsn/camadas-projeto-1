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
serialName = "COM5"                  # Windows(variacao de)

def float_to_ieee_754(float_value):
    return struct.pack('f', float_value)

def ieee_754_to_float(ieee_value):
    return struct.unpack('f', ieee_value)[0]

def rounder(x):
    '''
    Função que arredonda o número x para 6 casas decimais e retorna o número em notação científica
    '''
    concat_list = (str(x)).split('e')
    num = str(round(float(concat_list[0]), 6))
    exp = concat_list[1]
    num_complete = float(num + 'e' + exp)
    return num_complete

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        time.sleep(2)
        com1.sendData(b'00')
        time.sleep(1)


        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")
        
        #aqui você deverá gerar os dados a serem transmitidos. 
        #seus dados a serem transmitidos são um array bytes a serem transmitidos. Gere esta lista com o 
        #nome de txBuffer. Esla sempre irá armazenar os dados a serem enviados.

        # PROJETO 1
        # imgR = "./imgs/bmp.jpeg"
        # imgW = "./imgs/bmp_copy.jpeg"

        # print(f'Abrindo a imagem {imgR}')
        # print('--'*30)

        # #txBuffer = imagem em bytes!
        # txBuffer = open(imgR, 'rb').read()

        # PROJETO 2
        #n = random.randint(5, 15)
        #min_ = round(-1*(10**38), 6)
        #max_ = round(1*(10**38), 6)
        #txBuffer = [float_to_ieee_754(rounder(random.uniform(min_, max_))) for _ in range(n)]
        #print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
        
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        #print("enviando dados ....")
        #tente entender como o método send funciona!
        #Cuidado! Apenas trasmita arrays de bytes!
        
        #com1.sendData(np.asarray(txBuffer))  #as array apenas como boa pratica para casos de ter uma outra forma de dados

        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        #while not com1.tx.threadMutex:
        #    time.sleep(0.05)
        #txSize = com1.tx.getStatus()
        #print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.
        # Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        # #Veja o que faz a funcao do enlaceRX  getBufferLen

        # #acesso aos bytes recebidos

        print('esperando receber handshake')
        while True:
            len_rx = com1.rx.getBufferLen()
            if len_rx > 0:
                rxBuffer, nRx = com1.getData(15)
                print(f"Código de handshake recebido: {rxBuffer}")
                break
        print('devolvendo handshake')
        com1.sendData(np.asarray(rxBuffer))
        print('handshake devolvido')
        time.sleep(2)

        while True:
            len_rx = com1.rx.getBufferLen()
            if len_rx > 0:
                rxBuffer, nRx = com1.getData(15)
                print(f"Código de handshake recebido: {rxBuffer}")
                break

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
