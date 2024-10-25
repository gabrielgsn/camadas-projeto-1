from suaBibSignal import *
import peakutils   
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time



def todB(s):
    sdB = 10*np.log10(s)
    return(sdB)


def main():

    signal = signalMeu() 
       

    sd.default.samplerate = 44100
    sd.default.channels = 1 
    duration =  5 

    numAmostras = int(duration*sd.default.samplerate)
    freqDeAmostragem = sd.default.samplerate

    print("Gravacao comecando e 3 segundos")
    time.sleep(3)
    print("Gravando...")

    audio = sd.rec(int(numAmostras), freqDeAmostragem, channels=1)
    sd.wait()
    print("Gravacao finalizada")



    audio = audio[:, 0]
    t = np.linspace(0, duration, numAmostras)
    plt.figure()
    plt.plot(t[1000:], audio[1000:]) 
    plt.title("Áudio capturado - Domínio do Tempo")
    plt.xlabel("Tempo [s]")
    plt.ylabel("Amplitude")
    plt.show() 
    fs = 44100
    xf, yf = signal.calcFFT(audio, fs)   

    plt.figure()
    plt.plot(xf, yf)
    plt.title("Transformada de Fourier do Sinal Gravado")
    plt.xlabel("Frequência [Hz]")
    plt.ylabel("Magnitude")
    plt.show() 
    indexes = peakutils.indexes(yf, thres=0.15, min_dist=45)
    freqs_de_pico = xf[indexes]
    
    if len(indexes) < 5:
        print(f"Menos de 5 picos identificados ({len(indexes)} picos), ajustando parâmetros.")
        indexes = peakutils.indexes(yf, thres=0.05, min_dist=30)
        freqs_de_pico = xf[indexes]

    print("Frequências identificadas nos picos: ", freqs_de_pico)

    dtmf_frequencies = {
        '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
        '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
        '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
        '*': (941, 1209), '0': (941, 1336), '#': (941, 1477)
    }

    for tecla, (f1, f2) in dtmf_frequencies.items():
        if any(np.isclose(freqs_de_pico, f1, atol=5)) and any(np.isclose(freqs_de_pico, f2, atol=5)):
            print(f"A tecla pressionada foi: {tecla}")
            break

    plt.show()

if __name__ == "__main__":
    main()
