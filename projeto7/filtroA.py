import numpy as np
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
import time 
import sounddevice as sd
from suaBibSignal import *


def butter_lowpass(f_corte, fs, order=5):
    return butter(order, f_corte, fs=fs, btype='low', analog=False)

def butter_lowpass_filter(data, f_corte, fs, order=5):
    b, a = butter_lowpass(f_corte, fs, order=order)
    y = lfilter(b, a, data)
    return y


order = 11
fs = 48000     
f_corte = 1500  

b, a = butter_lowpass(f_corte, fs, order=2)
b2, a2 = butter_lowpass(f_corte, fs, order)
w, h = freqz(b, a, fs=fs, worN=8000)
w2, h2 = freqz(b2, a2, fs=fs, worN=8000)

signal = signalMeu() 
print("Gravacao comecando em 1 segundos")
time.sleep(1)
print("Gravando...")
audio = sd.rec(int(3*fs), fs, channels=1)
sd.wait()
print("Gravacao finalizada")

audio = audio[:, 0]
audio = np.random.normal(0,1,44100*3)
xf, yf = signal.calcFFT(audio, fs) 
saida = butter_lowpass_filter(audio, f_corte, fs, order)
xf2, yf2 = signal.calcFFT(saida, fs)

#plotando os graficos do sinal filtrado e do sinal gravado

plt.figure(figsize=(10, 10))
plt.subplot(2, 1, 1)
plt.plot(xf, yf)
plt.xlim(0, 0.1*fs)
plt.title("Transformada de Fourier do Sinal Gravado")
plt.xlabel("Frequência [Hz]")
plt.ylabel("Magnitude")
plt.subplot(2, 1, 2)
plt.plot(xf2, yf2)
plt.xlim(0, 0.1*fs)
plt.title("Transformada de Fourier do Sinal Filtrado")
plt.xlabel("Frequência [Hz]")
plt.ylabel("Magnitude")

# Plotando o grafico do passabaixa

plt.figure(figsize=(10, 7))
plt.subplot(2, 1, 1)
plt.plot(w, np.abs(h), 'b')
plt.plot(f_corte, 0.5*np.sqrt(2), 'ko')
plt.axvline(f_corte, color='k')
plt.xlim(0, 0.05*fs)
plt.title("Frequência filtrada de passabaixa")
plt.subplot(2, 1, 2)
plt.plot(w2, np.abs(h2), 'b')
plt.plot(f_corte, 0.5*np.sqrt(2), 'ko')
plt.axvline(f_corte, color='k')
plt.xlim(0, 0.05*fs)
plt.xlabel('Frequency [Hz]')
plt.show()