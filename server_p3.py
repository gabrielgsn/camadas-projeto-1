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

def analisa_Head(head):
    numeros=""
    info=[]
    i=1
    for byte in head:
        if i<2:
            numeros+=str(byte)
        else:
            numeros+=str(byte)
            info.append(int(numeros))
            numeros=""
            i=0
        i+=1
    return (info)

def cria_Head(msg_type, i, payload_len, len_payload):
    head = msg_type.to_bytes(2, byteorder='big')
    head += i.to_bytes(2, byteorder='big')
    head += payload_len.to_bytes(2, byteorder='big')
    head += len_payload.to_bytes(2, byteorder='big')
    head += b'\x00'*4
    return head

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
        tamanho_do_payload=50
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

        bytes_imagem=b''
        contador_de_pacotes=0
        print("Iniciando recebimento da imagem")
        while True:
            len_rx = com1.rx.getBufferLen()
            if len_rx > 0:
                print("Recebendo pacote")
                rxBuffer, nRx = com1.getData(tamanho_do_payload+15)
                info=analisa_Head(rxBuffer)
                tipo_de_mensagem=info[0]
                numero_do_pacote=info[1]
                tamanho_da_imagem=info[2]
                print(f'tipo_de_mensagem {tipo_de_mensagem}')
                print(f'numero_do_pacote {numero_do_pacote}')
                print(f'tipo_de_mensagem {tamanho_da_imagem}')
                print(f'tamanho_do_payload {tamanho_do_payload}')

                if tipo_de_mensagem==2:
                    if numero_do_pacote==contador_de_pacotes:
                        info_pacote=12+tamanho_do_payload
                        eop=rxBuffer[-3:]
                        if eop==b'\xFF\xFF\xFF':
                            bytes_imagem+=rxBuffer[12:info_pacote]
                            print(f"Recebendo pacote {numero_do_pacote}")
                            print("Mandando confirmação para o cliente")
                            confirmacao=cria_Head(0, numero_do_pacote, 0, 0)
                            com1.sendData(confirmacao)
                            time.sleep(2)
                            
                        else:
                            print("Erro no pacote")
                            print("Mandando erro para o cliente")
                            erro=cria_Head(1, numero_do_pacote, 0, 0)
                            com1.sendData(erro)
                            time.sleep(2)
                    else:
                        print("Pacote fora de ordem")
                        print("Mandando erro para o cliente")
                        erro=cria_Head(1, numero_do_pacote, 0, 0)
                        com1.sendData(erro)
                        time.sleep(2)
                else:
                    print("Tipo de mensagem errada")
                    print("Mandando erro para o cliente")
                    erro=cria_Head(1, numero_do_pacote, 0, 0)
                    com1.sendData(erro)
                    time.sleep(2)


                contador_de_pacotes+=1
                tamanho_do_payload=info[3]
                if contador_de_pacotes==tamanho_da_imagem:
                    print("Imagem recebida com sucesso")
                    txBuffer=b'\x00'*12
                    com1.sendData(txBuffer)
                    break
        
        imagem="./imgs/paulo_kogos_copy.jpeg"
        print(f"Salvando imagem em {imagem}")
        f=open(imagem, 'wb')
        f.write(bytes_imagem)
        f.close()
        print("Imagem salva com sucesso")


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
