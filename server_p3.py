from enlace import *
import time
import numpy as np
# import sys
import struct
import random
import crcmod
# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM5"                  # Windows(variacao de)

def calculate_crc16(data):
    func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, xorOut=0x0000)
    return func(data)
    
def analisa_Head(head):
    info=[]
    info.append(int.from_bytes(head[0:2],byteorder="big"))
    info.append(int.from_bytes(head[2:4],byteorder="big"))
    info.append(int.from_bytes(head[4:6],byteorder="big"))
    info.append(int.from_bytes(head[6:8],byteorder="big"))
    info.append(int.from_bytes(head[8:10],byteorder="big"))
    info.append(int.from_bytes(head[10:12],byteorder="big"))
    return (info)

def cria_Head(msg_type, i, payload_len, len_payload, crc=None):
    head = msg_type.to_bytes(2, byteorder='big')
    head += i.to_bytes(2, byteorder='big')
    head += payload_len.to_bytes(2, byteorder='big')
    head += len_payload.to_bytes(2, byteorder='big')
    head +=crc.to_bytes(2, byteorder='big') if crc else b'\x00'*2
    head += b'\x00'*2
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
        # n_pacote_anterior=None
        eop = b'\xFF\xFF\xFF'
        print("Iniciando recebimento da imagem")
        init_time = time.time()
        error=False
        while True:
            len_rx = com1.rx.getBufferLen()
            if len_rx > 0:
                init_time = time.time()
                recebimento=True
                print("----------------------------------------------")
                print("Recebendo pacote")
                print(f"recebendo dados do pacote {contador_de_pacotes}")
                rxBuffer, nRx = com1.getData(tamanho_do_payload+15)
                head=rxBuffer[:12]
                info=analisa_Head(head)
                tipo_de_mensagem=info[0]
                numero_do_pacote=info[1]
                tamanho_da_imagem=info[2]
                crc=info[4]
                print(f'tipo_de_mensagem {tipo_de_mensagem}')
                print(f'numero_do_pacote {numero_do_pacote}')
                print(f'tipo_de_mensagem {tamanho_da_imagem}')
                print(f'tamanho_do_payload {tamanho_do_payload}')
                print(f"crc = {crc}")
                # if numero_do_pacote==contador_de_pacotes+1:
                #     if numero_do_pacote-1==n_pacote_anterior:
                #         contador_de_pacotes+=1
                #         error=False
                        
                if tipo_de_mensagem==2:
                    if numero_do_pacote==contador_de_pacotes:
                        info_pacote=12+tamanho_do_payload
                        eop=rxBuffer[-3:]
                        if eop==b'\xFF\xFF\xFF':
                            if not error:
                                payload=rxBuffer[12:info_pacote]
                                bytes_imagem+=payload
                                crc_calculado=calculate_crc16(payload)
                                print(f"crc calculado foi {crc_calculado}")
                                if crc_calculado==crc:
                                    print(f"Recebendo pacote {numero_do_pacote}")
                                    print("Mandando confirmação para o cliente")
                                    confirmacao=cria_Head(0, numero_do_pacote, 0, 0)+eop
                                    print(confirmacao)
                                    com1.sendData(confirmacao)
                                    time.sleep(0.5)
                                else:
                                    print("Erro no pacote devido ao crc")
                                    print("Mandando erro para o cliente")
                                    erro=cria_Head(1, numero_do_pacote, 0, 0)+eop
                                    com1.sendData(erro)
                                    time.sleep(0.5)
                                    contador_de_pacotes-=1
                        else:
                            print("Erro no pacote")
                            print("Mandando erro para o cliente")
                            erro=cria_Head(1, numero_do_pacote, 0, 0)+eop
                            com1.sendData(erro)
                            time.sleep(0.5)
                            contador_de_pacotes-=1
                    else:
                        print("Pacote fora de ordem")
                        print("Mandando erro para o cliente")
                        erro=cria_Head(1, numero_do_pacote, 0, 0)+eop
                        com1.sendData(erro)
                        time.sleep(0.5)
                        contador_de_pacotes-=1
                else:
                    print("Tipo de mensagem errada")
                    print("Mandando erro para o cliente")
                    erro=cria_Head(1, numero_do_pacote, 0, 0)+eop
                    com1.sendData(erro)
                    time.sleep(0.5)
                    contador_de_pacotes-=1

                print("----------------------------------------------")
                contador_de_pacotes+=1
                tamanho_do_payload=info[3]
                # n_pacote_anterior=numero_do_pacote
                error=False
                if contador_de_pacotes==tamanho_da_imagem:
                    print("Imagem recebida com sucesso")
                    txBuffer=b'\x00'*12+eop
                    com1.sendData(txBuffer)
                    break

            if time.time() - init_time > 5  :
                if recebimento:
                    print(f"confirmação do pacote {contador_de_pacotes -1} não foi recebida")
                    contador_de_pacotes-=1
                    recebimento=False
                    error=True
                    init_time=time.time()
        
        imagem="camadas-projeto-1\imgs\imagem_teste_copy.jpg"
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
