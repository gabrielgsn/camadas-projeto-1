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
        # n = random.randint(5, 15)
        n = 3
        min_ = round(-1*(10**38), 6)
        max_ = round(1*(10**38), 6)
        
        txBuffer = [float_to_ieee_754(rounder(random.uniform(min_, max_))) for _ in range(n)]
        total = sum([ieee_754_to_float(i) for i in txBuffer])  # Exclude stop byte from sum
        print("Soma = {}" .format(total))
        print("meu array de bytes tem tamanho {}" .format(len(txBuffer)))
        #faça aqui uma conferência do tamanho do seu txBuffer, ou seja, quantos bytes serão enviados.
        
        #finalmente vamos transmitir os todos. Para isso usamos a funçao sendData que é um método da camada enlace.
        #faça um print para avisar que a transmissão vai começar.
        print("enviando dados ....")
        start_byte = b'\x00\x00\x00\x00'
        # check_byte = b'\x00\x00\x00\x00'
        stop_byte = b'\xFF\xFF\xFF\xFF'
        time.sleep(2)
        # com1.sendData(np.asarray(start_byte))
        time.sleep(2)
        for i in txBuffer:
            print(f'enviando: {ieee_754_to_float(i)}')
            com1.sendData(np.asarray(i))
            time.sleep(2)
        com1.sendData(np.asarray(stop_byte))
        
        
        
        # A camada enlace possui uma camada inferior, TX possui um método para conhecermos o status da transmissão
        # O método não deve estar fincionando quando usado como abaixo. deve estar retornando zero. Tente entender como esse método funciona e faça-o funcionar.
        time.sleep(2)
        com1.tx.threadMutex = True
        txSize = com1.tx.getStatus()
        print('enviou = {}' .format(txSize))
        
        #Agora vamos iniciar a recepção dos dados. Se algo chegou ao RX, deve estar automaticamente guardado
        #Observe o que faz a rotina dentro do thread RX
        #print um aviso de que a recepção vai começar.

        # print("Recebendo dados ....")
        
        # #Será que todos os bytes enviados estão realmente guardadas? Será que conseguimos verificar?
        # #Veja o que faz a funcao do enlaceRX  getBufferLen

        # #acesso aos bytes recebidos
        # txLen = len(txBuffer)
        # rxBuffer, nRx = com1.getData(txLen)
        # print("recebeu {} bytes" .format(len(rxBuffer)))
        
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
