from suaBibSignal import *
import peakutils
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time

def todB(s):
    sdB = 10 * np.log10(s)
    return sdB

def main():

    signal = signalMeu()

    a = 0.0004811
    b = 0.0004741
    d = -1.956
    e = 0.9568


    sd.default.samplerate = 48000  
    sd.default.channels = 1        
    duration = 3                   
    numAmostras = int(duration * sd.default.samplerate)
    freqDeAmostragem = sd.default.samplerate

    print("Gravação começando em 1 segundos")
    time.sleep(1)
    print("Gravando...")
    audio = sd.rec(numAmostras, freqDeAmostragem, channels=1)
    sd.wait()
    print("Gravação finalizada")

    audio = audio[:, 0]


    xf, yf = signal.calcFFT(audio, freqDeAmostragem)

    audio
    saida = [0, 0]
    for i in range(len(audio)):
        if i < 2:
            saida[i] = audio[i]
        else:
            saida.append(-d * saida[i-1] - e * saida[i-2] + a * audio[i-1] + b * audio[i-2])

    xfs, yfs = signal.calcFFT(saida, freqDeAmostragem)

    plt.figure()
    plt.plot(xfs, yfs)
    plt.title("Transformada de Fourier do Sinal Filtrado")
    plt.xlabel("Frequência [Hz]")
    plt.ylabel("Magnitude")
    plt.figure()
    plt.plot(xf, yf)
    plt.title("Transformada de Fourier do Sinal Gravado")
    plt.xlabel("Frequência [Hz]")
    plt.ylabel("Magnitude")
    plt.show()

if __name__ == "__main__":
    main()
