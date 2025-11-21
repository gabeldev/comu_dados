import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter, spectrogram

class Demultiplexador:
    def __init__(self):
        self.__fs = 44100
        self.__cutoff_baseband = 2000 # Ajustado para casar com o filtro do Mux
        self.__order = 6
        self.__carriers = {'A': 4000, 'B': 10000,'C': 14000}
        
        try:
            self.__muxed, self.__fs = sf.read("muxed_audio.wav")
            self.demultiplexar()
        except FileNotFoundError:
            print("Erro: Arquivo 'muxed_audio.wav' não encontrado.")

    # Filtro passa-faixa para isolar cada canal antes da demodulação (Item E)
    def bandpass_filter(self, signal, lowcut, highcut, fs, order):
        nyq = 0.5 * fs
        # Garante que não exceda Nyquist
        if highcut >= nyq: highcut = nyq - 1
        b, a = butter(order, [lowcut/nyq, highcut/nyq], btype='band')
        return lfilter(b, a, signal)

    def lowpass_filter(self, signal, cutoff, fs, order):
        nyq = 0.5 * fs
        b, a = butter(order, cutoff/nyq, btype='low')
        return lfilter(b, a, signal)

    def demodulate(self, signal, carrier_freq):
        t = np.arange(len(signal)) / self.__fs
        return signal * np.cos(2 * np.pi * carrier_freq * t)

    def normalize(self, signal):
        m = np.max(np.abs(signal))
        return signal / m if m > 0 else signal

    def demultiplexar(self):
        print("\nIniciando Demultiplexação (Item D)")
        for label, fc in self.__carriers.items():
            # Filtrar a banda do canal (fc +/- banda)
            band = self.bandpass_filter(self.__muxed, fc - self.__cutoff_baseband, fc + self.__cutoff_baseband, self.__fs, self.__order)
    
            # Demodular (Coerente)
            demod = self.demodulate(band, fc)
    
            # Filtro passa-baixa para remover a cópia em 2*fc
            baseband = self.lowpass_filter(demod, self.__cutoff_baseband, self.__fs, self.__order)
    
            # Salvar
            baseband_norm = self.normalize(baseband)
            sf.write(f"demux_channel_{label}.wav", baseband_norm, self.__fs)
            print(f"-> Canal {label} recuperado: 'demux_channel_{label}.wav'")
    
    def plota_espectro_multiplexador(self):
        N = len(self.__muxed)
        frequencias = fftfreq(N, 1/self.__fs)[:N//2]
        espectro = np.abs(fft(self.__muxed))[:N//2]

        plt.figure(figsize=(10, 4))
        plt.plot(frequencias, espectro)
        plt.title("Espectro do sinal multiplexado")
        plt.xlabel("Frequência (Hz)")
        plt.ylabel("Magnitude")
        plt.grid(True)
        plt.xlim(0, 16000)
        plt.show()

    def ler_pares(self, base_path, demux_path):
        base, fs1 = sf.read(base_path)
        demux, fs2 = sf.read(demux_path)
        assert fs1 == fs2, "Taxas de amostragem não coincidem"
        min_len = min(len(base), len(demux))
        return base[:min_len], demux[:min_len], fs1

    # Dicionário de pares: base e extraído
    def compara_espectro(self):
        canais = {'A': ("audio_A_base.wav", "demux_channel_A.wav"),
                'B': ("audio_B_base.wav", "demux_channel_B.wav"),
                'C': ("audio_C_base.wav", "demux_channel_C.wav")
                }
        
        # Gerar espectrogramas para cada canal
        for label, (base_path, demux_path) in canais.items():
            base, demux, fs = self.ler_pares(base_path, demux_path)

            fig, axs = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
            self.plota_spectrograma(base, fs, f"Original - Canal {label}", axs[0])
            self.plota_spectrograma(demux, fs, f"Demux - Canal {label}", axs[1])
            plt.tight_layout()
            plt.show()

    def plota_erros(self):
        #Plotar e comparar cada par
        canais = {'A': ("audio_A_base.wav", "demux_channel_A.wav"),
                'B': ("audio_B_base.wav", "demux_channel_B.wav"),
                'C': ("audio_C_base.wav", "demux_channel_C.wav")
                }
        for label, (base_path, demux_path) in canais.items():
            base, demux, fs = self.ler_pares(base_path, demux_path)
            
            # Calcular erro médio absoluto (MAE)
            mae = np.mean(np.abs(base - demux))
            
            # Plotar primeiros 1000 samples (~23 ms)
            plt.figure(figsize=(10, 3))
            plt.plot(base[:1000], label=f"Sinal original {label}", linewidth=1.5)
            plt.plot(demux[:1000], label=f"Demux {label}", linestyle='dashed', linewidth=1.2)
            plt.title(f"Comparação do Canal {label} - Erro Médio Absoluto: {mae:.6f}")
            plt.xlabel("Amostras")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    def comparar_sinais_visual(self):
        print("\nGerando Gráficos Comparativos (Item F)")
        canais = ['A', 'B', 'C']
        
        plt.figure(figsize=(12, 8))
        
        for i, label in enumerate(canais):
            original, fs1 = sf.read(f"audio_{label}_base.wav")
            recuperado, fs2 = sf.read(f"demux_channel_{label}.wav")
            
            # Garante mesmo tamanho para comparação
            min_len = min(len(original), len(recuperado))
            orig = original[:min_len]
            recup = recuperado[:min_len]
            
            # Cria subplot
            plt.subplot(3, 1, i+1)
            
            # Plota um trecho com 500 amostras para ver o detalhe da onda
            trecho = 500 
            plt.plot(orig[:trecho], label='Original', color='blue', alpha=0.7)
            plt.plot(recup[:trecho], label='Demultiplexado', color='red', linestyle='--', alpha=0.7)
            
            plt.title(f"Comparação Canal {label} (Primeiras {trecho} amostras)")
            plt.legend()
            plt.grid(True)
            
        
        plt.tight_layout()
        plt.show()